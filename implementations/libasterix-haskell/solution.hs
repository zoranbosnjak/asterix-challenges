{-# LANGUAGE DataKinds #-}
{-# LANGUAGE OverloadedStrings #-}

import Control.Monad
import Data.Maybe
import Data.Either
import Data.Word
import Data.Time.Clock
import Data.Map as Map
import Data.ByteString (ByteString)
import Options.Applicative

import Asterix.Coding
import Asterix.Generated as Gen

type Cat048 = Gen.Cat_048_1_32
type Cat062 = Gen.Cat_062_1_21
type Cat063 = Gen.Cat_063_1_7
type Cat065 = Gen.Cat_065_1_6

specs :: Map Word8 VRecord
specs = Map.fromList
    [ (48, schema @(RecordOf Cat048) Proxy)
    , (62, schema @(RecordOf Cat062) Proxy)
    , (63, schema @(RecordOf Cat063) Proxy)
    , (65, schema @(RecordOf Cat065) Proxy)
    ]

loadSamples :: FilePath -> IO [ByteString]
loadSamples path = do
    lst <- lines <$> readFile path
    case traverse unhexlify lst of
        Nothing -> error "Unable to read samples."
        Just val -> pure val

-- | Do nothing.
example0 :: [ByteString] -> Int
example0 _ = 0

-- | Number of decoding errors.
example1 :: [ByteString] -> Int
example1 = sum . fmap checkSample
  where
    checkSample :: ByteString -> Int
    checkSample rxBytes = fromRight 1 $ do
        rawDatablocks <- parseRawDatablocks rxBytes
        pure $ sum $ fmap checkDatablock rawDatablocks

    checkDatablock :: RawDatablock -> Int
    checkDatablock rawDb = case Map.lookup cat specs of
        Nothing -> 0 -- ignore unexpected category
        Just (GRecord sch) ->
            let act = parseRecords (GRecord sch)
                result = parse @StrictParsing act (getRawRecords rawDb)
            in either (const 1) (const 0) result
      where
        cat = rawDatablockCategory rawDb

-- | Number of valid records.
example2 :: [ByteString] -> Int
example2 = sum . fmap checkSample
  where
    checkSample :: ByteString -> Int
    checkSample rxBytes = fromRight 0 $ do
        rawDatablocks <- parseRawDatablocks rxBytes
        pure $ sum $ fmap checkDatablock rawDatablocks

    checkDatablock :: RawDatablock -> Int
    checkDatablock rawDb = case Map.lookup cat specs of
        Nothing -> 0 -- ignore unexpected category
        Just (GRecord sch) ->
            let act = parseRecords (GRecord sch)
                result = parse @StrictParsing act (getRawRecords rawDb)
            in either (const 0) length result
      where
        cat = rawDatablockCategory rawDb

-- | Custom item extraction.
example3 :: [ByteString] -> Word8
example3 = sum . fmap checkSample
  where
    checkSample :: ByteString -> Word8
    checkSample rxBytes = fromRight 0 $ do
        rawDatablocks <- parseRawDatablocks rxBytes
        pure $ sum $ fmap checkDatablock rawDatablocks

    checkDatablock :: RawDatablock -> Word8
    checkDatablock rawDb = fromRight 0 $ case rawDatablockCategory rawDb of
        48 -> do
            let act = parseRecords (schema @(RecordOf Cat048) Proxy)
            records <- fmap Record <$> parse @StrictParsing act (getRawRecords rawDb)
            pure $ sum $ fmap handleCat048 records
        62 -> do
            let act = parseRecords (schema @(RecordOf Cat062) Proxy)
            records <- fmap Record <$> parse @StrictParsing act (getRawRecords rawDb)
            pure $ sum $ fmap handleCat062 records
        _ -> pure 0

    handleCat048 :: Record (RecordOf Cat048) -> Word8
    handleCat048 r = maybe 0 asUint (getItem @"010" r >>= pure . getItem @"SAC")

    handleCat062 :: Record (RecordOf Cat062) -> Word8
    handleCat062 r = sum
        [ maybe 0 asUint (getItem @"015" r)
        , maybe 0 asUint (getItem @"010" r >>= pure . getItem @"SIC")
        , maybe 0 asUint (getItem @"080" r >>= getItem @"SRC" . getVariation)
        , maybe 0 asUint (getItem @"080" r >>= getItem @"MD5" . getVariation)
        , fromMaybe 0 $ do
            i510 <- getVariation <$> getItem @"510" r
            pure $ sum $ asUint . getItem @"IDENT" <$> getRepetitiveItems i510
        , maybe 0 asUint (getItem @"290" r >>= getItem @"MDS" . getVariation)
        ]

-- | Number of ‘spare’ bits abuses.
-- That is: number of times that spare bits are not zero.
example4 :: [ByteString] -> Int
example4 = sum . fmap checkSample
  where
    checkSample :: ByteString -> Int
    checkSample rxBytes = fromRight 0 $ do
        rawDatablocks <- parseRawDatablocks rxBytes
        pure $ sum $ fmap checkDatablock rawDatablocks

    checkDatablock :: RawDatablock -> Int
    checkDatablock rawDb = case Map.lookup cat specs of
        Nothing -> 0 -- ignore unexpected category
        Just (GRecord sch) -> fromRight 0 $ do
            let act = parseRecords (GRecord sch)
            records <- parse @StrictParsing act (getRawRecords rawDb)
            pure $ sum $ fmap (checkRecord sch) records
      where
        cat = rawDatablockCategory rawDb

    checkRecord :: [VUapItem] -> URecord -> Int
    checkRecord lst (URecord _bld items) = sum $ zipWith checkUapItem lst items

    checkUapItem :: VUapItem -> Maybe (RecordItem UNonSpare) -> Int
    checkUapItem sch mri = case (sch, mri) of
        (_, Nothing) -> 0
        (GUapItem sch1, Just (RecordItem nsp)) -> checkNonSpare sch1 nsp
        (GUapItemSpare, _ ) -> 0
        (GUapItemRFS, Just (RecordItem _)) -> error "TODO"
        _ -> error "internal error: unexpected result"

    checkNonSpare :: VNonSpare -> UNonSpare -> Int
    checkNonSpare (GNonSpare _name _title sch) (UNonSpare rv) = checkRuleVar sch rv

    checkRuleVar :: VRule VVariation -> URuleVar -> Int
    checkRuleVar sch (URuleVar var) = case sch of
        GContextFree sch1 -> checkVariation sch1 var
        GDependent _ sch1 _ -> checkVariation sch1 var

    checkVariation :: VVariation -> UVariation -> Int
    checkVariation sch var = case (sch, var) of
        (GElement {}, _) -> 0
        (GGroup _offset lst, UGroup items) -> sum $ zipWith checkItem lst items
        (GExtended lst, UExtended _bld mItems) ->
            let f :: Maybe VItem -> Maybe UItem -> Int
                f Nothing _ = 0
                f (Just _sch1) Nothing = 0
                f (Just sch1) (Just i) = checkItem sch1 i
            in sum $ zipWith f lst mItems
        (GRepetitive _rt sch1, URepetitive _bld vars) ->
            sum $ fmap (checkVariation sch1) vars
        (GExplicit _, _) -> 0
        (GCompound lst, UCompound _bld mNsps) ->
            let f :: Maybe (GNonSpare ValueLevel) -> Maybe UNonSpare -> Int
                f Nothing _ = 0
                f (Just _sch1) Nothing = 0
                f (Just sch1) (Just nsp) = checkNonSpare sch1 nsp
            in sum $ zipWith f lst mNsps
        _ -> error "internal error: unexpected result"

    checkItem :: VItem -> UItem -> Int
    checkItem (GSpare _o _n) (USpare b) = case bitsToNum @Int b of
        0 -> 0
        _ -> 1
    checkItem _ _ = 0

runExample :: Show a => Bool -> String -> a -> IO ()
runExample showTime example val = do
    when showTime $ print $ "--- " <> example <> " ---"
    t1 <- getCurrentTime
    print val
    t2 <- getCurrentTime
    when showTime $ print $ diffUTCTime t2 t1

data Options = Options
    { optTime :: Bool
    , optInput :: [FilePath]
    } deriving (Show, Eq)

options :: Parser Options
options = Options
    <$> switch
        ( long "time-it"
       <> short 't'
       <> help "Output timings"
        )
    <*> many ( strArgument ( metavar "PATH" ))

optsI :: ParserInfo Options
optsI = info (options <**> helper)
      ( fullDesc
     <> progDesc "Haskell implementation"
     <> header "test..."
      )

main :: IO ()
main = do
    opts <- execParser optsI
    samples <- mconcat <$> traverse loadSamples (optInput opts)
    let timeIt :: Show a => String -> a -> IO ()
        timeIt = runExample (optTime opts)
    timeIt "example0" $ example0 samples
    timeIt "example1" $ example1 samples
    timeIt "example2" $ example2 samples
    timeIt "example3" $ example3 samples
    timeIt "example4" $ example4 samples

