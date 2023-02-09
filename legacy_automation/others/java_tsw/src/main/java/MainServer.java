import httpd.NanoHTTPD;
import httpd.ServerRunner;


import java.util.HashMap;
import java.util.List;
import java.util.Map;


public class MainServer extends NanoHTTPD {
    private TSAServiceHandler serviceHandle = new TSAServiceHandler();
    public MainServer() throws Exception {
        super(Integer.parseInt(System.getProperty("port").trim()));
//        super(8090);
    }

    public static void main(String[] args) {
        ServerRunner.run(MainServer.class);
    }

    @Override public Response serve(IHTTPSession session) {
        String uri = session.getUri();
        if (uri.equals("/debug") || uri.startsWith("/debug/")){
            return getDebugServiceResponse(session);
        }
        if (uri.equals("/test") || uri.startsWith("/test/")){
            return new Response(Response.Status.OK, NanoHTTPD.MIME_PLAINTEXT, "{\"status\":\"pass\",\"data\":\"Server is up!\"}");
        }
        else {
            return serviceHandle.serve(session);
        }
    }

    Response getDebugServiceResponse(NanoHTTPD.IHTTPSession session){
        Map<String, List<String>> decodedQueryParameters = decodeParameters(session.getQueryParameterString());
        String uri = session.getUri();
        StringBuilder sb = new StringBuilder();
        sb.append("<html><head><title>Debug Mode</title></head><body><h1>Debug Server</h1>");
        sb.append("URL is " + new String(uri));

        sb.append("<p><blockquote><b>URI</b> = ").append(
                String.valueOf(session.getUri())).append("<br />");
        sb.append("<b>Method</b> = ").append(
                String.valueOf(session.getMethod())).append("</blockquote></p>");
        sb.append("<h3>Headers</h3><p><blockquote>").
                append(toString(session.getHeaders())).append("</blockquote></p>");
        sb.append("<h3>Parms</h3><p><blockquote>").
                append(toString(session.getParms())).append("</blockquote></p>");
        sb.append("<h3>Parms (multi values?)</h3><p><blockquote>").
                append(toString(decodedQueryParameters)).append("</blockquote></p>");
        try {
            Map<String, String> files = new HashMap<String, String>();
            session.parseBody(files);
            sb.append("<h3>Files</h3><p><blockquote>").
                    append(toString(files)).append("</blockquote></p>");
        } catch (Exception e) {
            e.printStackTrace();
        }
        sb.append("</body></html>");

        return new Response(sb.toString());
    }

    private String toString(Map<String, ? extends Object> map) {
        if (map.size() == 0) {
            return "";
        }
        return unsortedList(map);
    }

    private String unsortedList(Map<String, ? extends Object> map) {
        StringBuilder sb = new StringBuilder();
        sb.append("<ul>");
        for (Map.Entry entry : map.entrySet()) {
            listItem(sb, entry);
        }
        sb.append("</ul>");
        return sb.toString();
    }

    private void listItem(StringBuilder sb, Map.Entry entry) {
        sb.append("<li><code><b>").append(entry.getKey()).
                append("</b> = ").append(entry.getValue()).append("</code></li>");
    }

}