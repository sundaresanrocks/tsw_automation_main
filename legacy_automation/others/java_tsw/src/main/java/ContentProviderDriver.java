package com.securecomputing.sftools.harvester.devutils;

import com.securecomputing.sftools.harvester.interfaces.IContentProvider;
import com.securecomputing.sftools.harvester.util.HarvesterProperties;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.map.ObjectWriter;

import java.io.File;
import java.util.List;

/**
 * Created by mfinger on 2/24/14.
 */
public final class ContentProviderDriver {

    /** Private constructor. */
    private ContentProviderDriver() {

    }

    /**
     * Main execution routine.
     *
     * @param args Command line arguments
     * @throws Exception Any errors
     */
    public static void main(final String[] args) throws Exception {
        if (0 == args.length) {
            System.out.println("Args: harvester_properties class_name [output_file_name]");
        }
        int arg = 0;
        String harvesterProprties = args[arg++];
        String className = args[arg++];
        String outputFilename = null;
        if (args.length > 2) {
            outputFilename = args[arg++];
        }

        HarvesterProperties.loadProperties(harvesterProprties);

        Class<?> providerClass = ClassLoader.getSystemClassLoader().loadClass(className);
        IContentProvider providerInstance = (IContentProvider) providerClass.newInstance();
        providerInstance.initialize();
        List<String> files = providerInstance.getContent();

        ObjectMapper mapper = new ObjectMapper();
        mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.JAVA_LANG_OBJECT);
        @SuppressWarnings("deprecation")
        ObjectWriter writer = mapper.defaultPrettyPrintingWriter();
        System.out.println(writer.writeValueAsString(files));
        if (null != outputFilename) {
            File file = new File(outputFilename);
            writer.writeValue(file, files);
        }
    }
}
