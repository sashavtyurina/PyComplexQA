import java.nio.file.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.io.FileOutputStream;
import java.io.FileNotFoundException;

import java.nio.channels.AsynchronousServerSocketChannel;
import java.nio.channels.AsynchronousSocketChannel;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.AsynchronousServerSocketChannel;
import java.nio.channels.AsynchronousSocketChannel;
import java.nio.channels.CompletionHandler;
import java.nio.charset.Charset;
import java.util.concurrent.*;

import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.Term;
import org.apache.lucene.index.IndexOptions;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.store.Directory;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.analysis.util.CharArraySet;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.FieldType;


public class LuceneServer {
    private static String indexPath = "/home/avtyurin/Anserini/lucene-index.cw09b_pos.cnt/";
    private static IndexReader indexReader;
    private static String FIELD_BODY = "contents";
    private static String FIELD_ID = "id";

    /// sets up a connection with the index
    public static void setUpIndex(String index_path) {
        try {
            Path indexPath = Paths.get(index_path);
            indexReader = DirectoryReader.open(FSDirectory.open(indexPath));
        } catch (IOException e) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage() );
        }
    }

    /// returns a total number of occurences of the term in the corpus
    public static long totalTermFreq(String term) {
        long total = -1;
        try {
            /// ! note that the term is stemmed prior to being searched
            QueryParser queryParser = new QueryParser(FIELD_BODY, new EnglishAnalyzer(CharArraySet.EMPTY_SET));
            Query query = queryParser.parse(term);
            String analysed_query = query.toString(FIELD_BODY);
            System.out.println(analysed_query);
            Term t = new Term(FIELD_BODY, analysed_query);
            total = indexReader.totalTermFreq(t);
        } catch (IOException e) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage());
        } catch (ParseException e) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage());
        }
        return total;
    }

    /// returns total number of words in the corpus
    public static long totalTerms() {
        long total = -1;
        try {
            total = indexReader.getSumDocFreq(FIELD_BODY);
        } catch (IOException e){
            System.err.println( e.getClass().getName() + ": " + e.getMessage());
        }
        return total;
    }

    public static void main(String[] args) {
        setUpIndex(indexPath);
        calulateWordsFrequency("distinctWordsQA.txt");
    }

    /// adds another text document to the existing index
    /// here for test purposes
    public static void addDocToIndex(String docText, String docID, String pathToIndex) {

        try {
            Path indexPath = Paths.get(pathToIndex);
            final Directory dir = FSDirectory.open(indexPath);

            /// set up index writer
            final IndexWriterConfig iwc = new IndexWriterConfig(new EnglishAnalyzer(CharArraySet.EMPTY_SET));
            iwc.setSimilarity(new BM25Similarity());
            iwc.setOpenMode(IndexWriterConfig.OpenMode.APPEND);
            iwc.setRAMBufferSizeMB(512);
            final IndexWriter writer = new IndexWriter(dir, iwc);

            // set store term vectors to true
            FieldType fieldType = new FieldType();
            fieldType.setStoreTermVectors(true);
            fieldType.setTokenized(true);
            fieldType.setStored(true);
            fieldType.setStoreTermVectorPositions(true);
            fieldType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS_AND_OFFSETS);

            // make a new, empty document
            Document document = new Document();
            document.add(new StringField(FIELD_ID, docID, Field.Store.YES));
            document.add(new Field(FIELD_BODY, docText, fieldType));
            System.out.println(document.toString());
            writer.addDocument(document);
            writer.close();

        } catch (IOException e) {
          System.err.println( e.getClass().getName() + ": " + e.getMessage());
        }
    }

    /// given a file with words, complements it with corpus frequencies
    public static void calulateWordsFrequency(String filename) {
        try {
            BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(filename)));
            String nextLine;
            List<String> words = new ArrayList<String>();
            while ((nextLine = reader.readLine()) != null) {
                String word = nextLine.trim();
                words.add(word);
            }
            reader.close();

            PrintWriter writer = new PrintWriter(new FileOutputStream(filename));
            long total = totalTerms();
            for (String word : words) {
                long freq = totalTermFreq(word);
                writer.println(word + "|" + freq + "|" + total);
            }
            writer.close();
        } catch (FileNotFoundException e) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage());
        } catch (IOException e) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage());
        }

    }

}

