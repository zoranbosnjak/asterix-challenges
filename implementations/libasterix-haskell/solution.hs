{-# LANGUAGE DataKinds            #-}
{-# LANGUAGE LambdaCase           #-}
{-# LANGUAGE OverloadedStrings    #-}
{-# LANGUAGE UndecidableInstances #-}

module Main where

import           Control.Monad
import           Data.Aeson             (FromJSON, Object, Result (..), ToJSON,
                                         Value (..), decodeStrict, encode,
                                         fromJSON, object)
import qualified Data.Aeson.KeyMap      as KM
import           Data.ByteString        (ByteString)
import qualified Data.ByteString        as BS
import qualified Data.ByteString.Base16 as B16
import qualified Data.ByteString.Char8  as BS8
import qualified Data.ByteString.Lazy   as BSL
import           Data.Either
import           Data.Function          ((&))
import           Data.Map               as Map
import           Data.Maybe
import qualified Data.Scientific
import           Data.Text              (Text)
import qualified Data.Text              as T
import qualified Data.Text.IO           as T
import qualified Data.Vector            as Vec
import           Data.Word
import           Options.Applicative
import           System.Exit            (die)
import           System.IO
import           Text.Printf

import           Asterix.Coding
import           Asterix.Generated      as Gen

hexlify :: ByteString -> ByteString
hexlify = B16.encode

unhexlify :: ByteString -> Maybe ByteString
unhexlify st = either (const Nothing) Just (B16.decode st)

type Cat062 = Gen.Cat_062_1_21
type Cat063 = Gen.Cat_063_1_7
type Cat065 = Gen.Cat_065_1_6

specs :: Map Word8 VRecord
specs = Map.fromList
    [ (62, schema @(RecordOf Cat062) Proxy)
    , (63, schema @(RecordOf Cat063) Proxy)
    , (65, schema @(RecordOf Cat065) Proxy)
    ]

data Filter s a b = Filter
    { stepInput   :: s -> a -> (b, s)   -- run on valid input
    , stepInvalid :: s -> (b, s)      -- run on invalid input
    }

-- | Helper function to create a simple filter
arrFilter :: (a -> b) -> b -> Filter s a b
arrFilter f val = Filter
    { stepInput = \s x -> (f x, s)
    , stepInvalid = \s -> (val, s)
    }

-- | Helper function for parsing datablocks.
onDatablock :: (RawDatablock -> b) -> ByteString -> Maybe [b]
onDatablock f s = case parseRawDatablocks s of
    Left _e   -> Nothing
    Right lst -> Just $ fmap f lst

-- WJLXIXEB - identity filter
chWJLXIXEB :: Filter () ByteString ByteString
chWJLXIXEB = arrFilter id mempty

-- TXHWAQHG - determine length of input
chTXHWAQHG :: Filter () ByteString Int
chTXHWAQHG = arrFilter BS.length (-1)

-- GCMEDPFW - encode constant datagram
chGCMEDPFW :: Filter () Int ByteString
chGCMEDPFW = arrFilter (`BS.replicate` 0) mempty

-- CAOXOESE - decode first level of asterix
chCAOXOESE :: Filter () ByteString (Maybe [[Int]])
chCAOXOESE = arrFilter (onDatablock f) Nothing where
    f (RawDatablock s) =
        let cat = fromIntegral $ BS.index s 0
            n = fromIntegral (BS.index s 1) * 256 + fromIntegral (BS.index s 2)
        in [cat, n]

-- JWOONFHI - encode first level of asterix
chJWOONFHI :: Filter () [[Int]] ByteString
chJWOONFHI = arrFilter (maybe mempty mconcat . mapM f) mempty where
    f :: [Int] -> Maybe ByteString
    f x = do
        guard $ length x == 2
        let cat = x !! 0
            n = x !! 1
            (n1, n2) = divMod n 256
        guard $ cat >= 0 && cat < 256
        guard $ n >= 3 && n < 0x10000
        pure $
            BS.singleton (fromIntegral cat)
         <> BS.singleton (fromIntegral n1)
         <> BS.singleton (fromIntegral n2)
         <> BS.replicate (n-3) 0

-- FCYKLBBQ - reverse datablocks
chFCYKLBBQ :: Filter () ByteString ByteString
chFCYKLBBQ = arrFilter f mempty where
    f s = case parseRawDatablocks s of
        Left _e   -> mempty
        Right lst -> mconcat (unRawDatablock <$> reverse lst)

-- MVQCOXZJ - full asterix record decoding, count records
chMVQCOXZJ :: Filter () ByteString (Maybe [Maybe Int])
chMVQCOXZJ = arrFilter (onDatablock checkDatablock) Nothing where
    checkDatablock :: RawDatablock -> Maybe Int
    checkDatablock rawDb = fromRight Nothing $ case rawDatablockCategory rawDb of
        62 -> do
            let act = parseRecords (schema @(RecordOf Cat062) Proxy)
            Just . length <$> parse @StrictParsing act (getRawRecords rawDb)
        63 -> do
            let act = parseRecords (schema @(RecordOf Cat063) Proxy)
            Just . length <$> parse @StrictParsing act (getRawRecords rawDb)
        65 -> do
            let act = parseRecords (schema @(RecordOf Cat065) Proxy)
            Just . length <$> parse @StrictParsing act (getRawRecords rawDb)
        _ -> pure $ Just (-1)


-- VNRPNTIV - make single record datablocks
chVNRPNTIV :: Filter () ByteString ByteString
chVNRPNTIV = arrFilter f mempty where
    f :: ByteString -> ByteString
    f s = case parseRawDatablocks s of
        Left _   -> s
        Right lst -> mconcat $ fmap g lst
    g :: RawDatablock -> ByteString
    g rawDb = fromMaybe (toByteString $ unparse @SBuilder rawDb) $ do
        let cat = rawDatablockCategory rawDb
        act <- case cat of
            62 -> Just $ parseRecords (schema @(RecordOf Cat062) Proxy)
            63 -> Just $ parseRecords (schema @(RecordOf Cat063) Proxy)
            65 -> Just $ parseRecords (schema @(RecordOf Cat065) Proxy)
            _ -> Nothing
        records <- case parse @StrictParsing act (getRawRecords rawDb) of
            Left _ -> Nothing
            Right lst -> pure lst
        pure $ toByteString $ mconcat (datablockBuilder cat . pure <$> records)

-- CQNBMHNB - asterix record item extraction to json
chCQNBMHNB :: Filter () ByteString (Maybe [Maybe [Value]])
chCQNBMHNB = arrFilter (onDatablock checkDatablock) Nothing where
    checkDatablock :: RawDatablock -> Maybe [Value]
    checkDatablock rawDb = case rawDatablockCategory rawDb of
        62 -> do
            let act = parseRecords (schema @(RecordOf Cat062) Proxy)
                result = parse @StrictParsing act (getRawRecords rawDb)
            case result of
                Left _        -> Nothing
                Right records -> Just (checkRecord062 . Record <$> records)
        63 -> do
            let act = parseRecords (schema @(RecordOf Cat063) Proxy)
                result = parse @StrictParsing act (getRawRecords rawDb)
            case result of
                Left _        -> Nothing
                Right records -> Just (checkRecord063 . Record <$> records)
        65 -> do
            let act = parseRecords (schema @(RecordOf Cat065) Proxy)
                result = parse @StrictParsing act (getRawRecords rawDb)
            case result of
                Left _        -> Nothing
                Right records -> Just (checkRecord065 . Record <$> records)
        _ -> Nothing

    checkRecord062 :: Record (RecordOf Cat062) -> Value
    checkRecord062 r = object
        [ ("I062/015", i015)
        , ("I062/010/SAC", iSAC)
        , ("I062/080/SRC", iSRC)
        , ("I062/080/MD5", iMD5)
        , ("I062/510/IDENT", iIDENT)
        , ("I062/290/MDS", iMDS)
        ]
      where
        i015 = maybe Null (Number . fromIntegral @Int . asUint)
            (getItem @"015" r)
        iSAC = maybe Null (Number . fromIntegral @Int . asUint)
            (getItem @"010" r >>= pure . getItem @"SAC")
        iSRC = maybe Null (Number . fromIntegral @Int . asUint)
            (getItem @"080" r >>= getItem @"SRC" . getVariation)
        iMD5 = maybe Null (Number . fromIntegral @Int . asUint)
            (getItem @"080" r >>= getItem @"MD5" . getVariation)
        iIDENT = maybe Null (Array . Vec.fromList) $ do
            i510 <- getVariation <$> getItem @"510" r
            Just $ Number . fromIntegral @Int . asUint
                . getItem @"IDENT" <$> getRepetitiveItems i510
        iMDS = maybe Null (Number . fromIntegral @Int . asUint)
            (getItem @"290" r >>= getItem @"MDS" . getVariation)

    checkRecord063 :: Record (RecordOf Cat063) -> Value
    checkRecord063 r = object
        [ ("I063/010/SIC", iSIC)
        ]
      where
        iSIC = maybe Null (Number . fromIntegral @Int . asUint)
            (getItem @"010" r >>= pure . getItem @"SIC")

    checkRecord065 :: Record (RecordOf Cat065) -> Value
    checkRecord065 r = object
        [ ("I065/000", i000)
        ]
      where
        i000 = maybe Null (Number . fromIntegral @Int . asUint)
            (getItem @"000" r)

-- asterix record construction
chRWVTCOAU :: Filter () Value ByteString
chRWVTCOAU = arrFilter f mempty where
    f :: Value -> ByteString
    f val = fromMaybe mempty $ do
        o <- case val of
            Object o -> pure o
            _        -> Nothing
        cat <- KM.lookup "cat" o >>= \case
            Number x -> pure x
            _ -> Nothing
        case cat of
            62 -> do
                let db :: Datablock (DatablockOf Cat062) = datablock (r *: nil)
                    lookupInteger :: KM.Key -> Object -> Maybe Integer
                    lookupInteger key o2 = KM.lookup key o2 >>= \case
                        Number x -> do
                            guard $ Data.Scientific.isInteger x
                            pure $ round x
                        _ -> Nothing
                    getSubitem510 ::
                        ( nsp ~ (RecordOf Cat062 ~> "510")
                        , nsp ~ 'GNonSpare name title rv
                        , rv ~ 'GContextFree ('GRepetitive rt var)
                        )
                        => Value
                        -> Maybe (Variation var)
                    getSubitem510 = \case
                        Object o2 -> do
                            iIDENT <- lookupInteger "IDENT" o2
                            iTRACK <- lookupInteger "TRACK" o2
                            pure $ group
                                ( item @"IDENT" (fromInteger iIDENT)
                               *: item @"TRACK" (fromInteger iTRACK)
                               *: nil)
                        _ -> Nothing
                    r = record nil
                        & maybeSetItem @"010" (lookupItem fromInteger o "010")
                        & maybeSetItem @"040" (lookupItem fromInteger o "040")
                        & maybeSetItem @"290" (do
                            x <- lookupItem fromInteger o "290/PSR"
                            Just $ compound (item @"PSR" x *: nil)
                            )
                        & maybeSetItem @"510" (do
                            lst1 <- lookupItem id o "510"
                            lst2 <- mapM getSubitem510 lst1
                            Just $ repetitive lst2
                            )
                        & maybeSetItem @"380" (do
                            lst <- lookupItem (fmap fromInteger) o "380/BDSDATA"
                            Just $ compound
                                (item @"BDSDATA" ( repetitive lst) *: nil)
                            )
                Just $ toByteString $ unparse @SBuilder db
            63 -> do
                let db :: Datablock (DatablockOf Cat063) = datablock (r *: nil)
                    r = record nil
                        & maybeSetItem @"010" (lookupItem fromInteger o "010")
                        & maybeSetItem @"015" (lookupItem fromInteger o "015")
                Just $ toByteString $ unparse @SBuilder db
            65 -> do
                let db :: Datablock (DatablockOf Cat065) = datablock (r *: nil)
                    r = record nil
                        & maybeSetItem @"010" (lookupItem fromInteger o "010")
                        & maybeSetItem @"020" (lookupItem fromInteger o "020")
                Just $ toByteString $ unparse @SBuilder db
            _ -> Nothing
      where
        lookupItem convert o key = fromJSON <$> KM.lookup key o >>= \case
            Error _ -> Nothing
            Data.Aeson.Success i -> Just $ convert i

-- spare bits abuse detection
chAYTIGDAT :: Filter () ByteString Bool
chAYTIGDAT = arrFilter (maybe False or . onDatablock checkDatablock) False
  where
    checkDatablock :: RawDatablock -> Bool
    checkDatablock rawDb = case Map.lookup cat specs of
        Nothing -> False
        Just (GRecord sch) ->
            let act = parseRecords (GRecord sch)
                result = parse @StrictParsing act (getRawRecords rawDb)
            in case result of
                Left _        -> False
                Right records -> any (checkRecord sch) records
      where
        cat = rawDatablockCategory rawDb

    checkRecord :: [VUapItem] -> URecord -> Bool
    checkRecord lst (URecord _bld items) = or $ zipWith checkUapItem lst items

    checkUapItem :: VUapItem -> Maybe (RecordItem UNonSpare) -> Bool
    checkUapItem sch mri = case (sch, mri) of
        (_, Nothing) -> False
        (GUapItem sch1, Just (RecordItem nsp)) -> checkNonSpare sch1 nsp
        (GUapItemSpare, _ ) -> False
        (GUapItemRFS, Just (RecordItem _)) -> error "TODO"
        _ -> error "internal error: unexpected result"

    checkNonSpare :: VNonSpare -> UNonSpare -> Bool
    checkNonSpare (GNonSpare _name _title sch) (UNonSpare rv) = checkRuleVar sch rv

    checkRuleVar :: VRule VVariation -> URuleVar -> Bool
    checkRuleVar sch (URuleVar var) = case sch of
        GContextFree sch1   -> checkVariation sch1 var
        GDependent _ sch1 _ -> checkVariation sch1 var

    checkVariation :: VVariation -> UVariation -> Bool
    checkVariation sch var = case (sch, var) of
        (GElement {}, _) -> False
        (GGroup _offset lst, UGroup items) -> or $ zipWith checkItem lst items
        (GExtended lst, UExtended _bld mItems) ->
            let f :: Maybe VItem -> Maybe UItem -> Bool
                f Nothing _            = False
                f (Just _sch1) Nothing = False
                f (Just sch1) (Just i) = checkItem sch1 i
            in or $ zipWith f lst mItems
        (GRepetitive _rt sch1, URepetitive _bld vars) ->
            any (checkVariation sch1) vars
        (GExplicit _, _) -> False
        (GCompound lst, UCompound _bld mNsps) ->
            let f :: Maybe (GNonSpare ValueLevel) -> Maybe UNonSpare -> Bool
                f Nothing _              = False
                f (Just _sch1) Nothing   = False
                f (Just sch1) (Just nsp) = checkNonSpare sch1 nsp
            in or $ zipWith f lst mNsps
        _ -> error "internal error: unexpected result"

    checkItem :: VItem -> UItem -> Bool
    checkItem (GSpare _o _n) (USpare b) = bitsToNum @Int b /= 0
    checkItem _ _                       = False

-- conversion to 'quantity'
chRKMIVFTJ :: Filter () ByteString [String]
chRKMIVFTJ = arrFilter (maybe [] join . onDatablock checkDatablock) [] where
    checkDatablock :: RawDatablock -> [String]
    checkDatablock rawDb = case rawDatablockCategory rawDb of
        62 -> do
            let act = parseRecords (schema @(RecordOf Cat062) Proxy)
                result = parse @StrictParsing act (getRawRecords rawDb)
            case result of
                Left _        -> []
                Right records -> catMaybes
                    [checkRecord062 (Record r) | r <- records]
        _ -> []
      where
        checkRecord062 :: Record (RecordOf Cat062) -> Maybe String
        checkRecord062 r = do
            i070 <- getItem @"070" r
            pure $ printf "%.3f" $ unQuantity $ asQuantity @"s" i070

-- conversion from 'quantity'
chBIQUTYDD :: Filter () [Double] ByteString
chBIQUTYDD = arrFilter f mempty where
    f :: [Double] -> ByteString
    f = toByteString . datablockBuilder @Int 62 . fmap (unRecord . mkRecord)

    mkRecord :: Double -> Record (RecordOf Cat062)
    mkRecord val = record
        ( item @"010" 0x1234
       *: item @"070" (quantity @"s" $ Quantity val)
       *: nil )

-- conversion to 'string'
chKUPKVSJU :: Filter () ByteString [String]
chKUPKVSJU = arrFilter (maybe [] join . onDatablock checkDatablock) [] where
    checkDatablock :: RawDatablock -> [String]
    checkDatablock rawDb = case rawDatablockCategory rawDb of
        62 -> do
            let act = parseRecords (schema @(RecordOf Cat062) Proxy)
                result = parse @StrictParsing act (getRawRecords rawDb)
            case result of
                Left _        -> []
                Right records -> join
                    [checkRecord062 (Record r) | r <- records]
        _ -> []
      where
        checkRecord062 :: Record (RecordOf Cat062) -> [String]
        checkRecord062 r = catMaybes [i060, i380, i390]
          where
            i060 = do
                i <- getItem @"060" r
                pure $ asString $ getItem @"MODE3A" i
            i380 = do
                i <- getItem @"380" r
                j <- getItem @"ID" $ getVariation i
                pure $ asString j
            i390 = do
                i <- getItem @"390" r
                j <- getItem @"CS" $ getVariation i
                pure $ asString j


class Input t where
    convertInput :: ByteString -> Maybe t

instance FromJSON t => Input t where
    convertInput = decodeStrict

instance {-# OVERLAPPING #-} Input ByteString where
    convertInput = Main.unhexlify

class Output t where
    convertOutput :: t -> ByteString

instance ToJSON t => Output t where
    convertOutput = BSL.toStrict . encode

instance {-# OVERLAPPING #-} Output ByteString where
    convertOutput = Main.hexlify

runFilter :: (Input a, Output b) => s -> Filter s a b -> IO ()
runFilter initialState (Filter f1 f2) = go initialState where
    go s = isEOF >>= \case
        True -> pure ()
        False -> do
            (y, s') <- convertInput <$> BS8.getLine >>= \case
                Nothing -> pure $ f2 s
                Just x -> pure $ f1 s x
            BS8.putStrLn $ convertOutput y
            hFlush stdout
            go s'

solutions :: [(Text, IO ())]
solutions =
    [ ("WJLXIXEB", runFilter () chWJLXIXEB)
    , ("TXHWAQHG", runFilter () chTXHWAQHG)
    , ("GCMEDPFW", runFilter () chGCMEDPFW)
    , ("CAOXOESE", runFilter () chCAOXOESE)
    , ("JWOONFHI", runFilter () chJWOONFHI)
    , ("FCYKLBBQ", runFilter () chFCYKLBBQ)
    , ("MVQCOXZJ", runFilter () chMVQCOXZJ)
    , ("VNRPNTIV", runFilter () chVNRPNTIV)
    , ("CQNBMHNB", runFilter () chCQNBMHNB)
    , ("RWVTCOAU", runFilter () chRWVTCOAU)
    , ("AYTIGDAT", runFilter () chAYTIGDAT)
    , ("RKMIVFTJ", runFilter () chRKMIVFTJ)
    , ("BIQUTYDD", runFilter () chBIQUTYDD)
    , ("KUPKVSJU", runFilter () chKUPKVSJU)
    ]

data Command
    = ShowManifest
    | RunChallenge Text
    deriving (Show, Eq)

newtype Options = Options
    { optCommand :: Command
    } deriving (Show, Eq)

pShowManifest :: ParserInfo Command
pShowManifest = info (pure ShowManifest) idm

pRunChallenge :: ParserInfo Command
pRunChallenge = info p idm where
    p = RunChallenge
        <$> strArgument
            ( help "challenge identifier"
           <> metavar "ID"
            )

options :: Parser Options
options = Options
    <$> hsubparser
        ( command "manifest" pShowManifest
       <> command "run" pRunChallenge
        )

optsI :: ParserInfo Options
optsI = info (options <**> helper)
      ( fullDesc
     <> progDesc "Haskell implementation"
     <> header "test..."
      )

main :: IO ()
main = (optCommand <$> execParser optsI) >>= \case
    ShowManifest -> mapM_ (T.putStrLn . fst) solutions
    RunChallenge identifier -> case Prelude.lookup identifier solutions of
        Nothing  -> die (T.unpack identifier <> " not implemented!")
        Just act -> act

