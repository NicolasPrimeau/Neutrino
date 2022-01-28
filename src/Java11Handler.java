package com.neutrino.handlers;
import java.io.File;
import java.io.FileWriter;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Map;
import java.util.HashMap;
import java.util.List;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.io.IOException;
import java.lang.RuntimeException;
import java.net.URL;

import javax.tools.JavaCompiler;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.StandardJavaFileManager;
import javax.tools.StandardLocation;
import javax.tools.ToolProvider;
import javax.tools.JavaFileObject;
import java.net.URLClassLoader;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.PrintStream;

class Response {
    private Gson gson = new GsonBuilder().setPrettyPrinting().create();
    public int statusCode;
    public Map<String, String> headers;
    public String body;

    Response(int statusCode, String stdout, String stderr) {
        this.statusCode = statusCode;
        this.headers = new HashMap<>();
        this.headers.put("Access-Control-Allow-Origin", "*");

        Map<String, String> body = new HashMap<>();
        body.put("stdout", stdout);
        body.put("stderr", stderr);

        this.body = gson.toJson(body);
    }

}

class Request {
    public String body;
}


public class Handler implements RequestHandler<Request, Response>{
  Gson gson = new GsonBuilder().setPrettyPrinting().create();

  private static String compileErrorMessage = "";

  @Override
  public Response handleRequest(Request event, Context context)
  {
    compileErrorMessage = "";

    Map<String, String> body = gson.fromJson(event.body, Map.class);
    try {
        String sourceCode = body.get("source_code");
        File sourceFile = new File("/tmp/Main.java");
        FileWriter writer = new FileWriter(sourceFile);
        writer.write(sourceCode);
        writer.close();

        File parentDirectory = loadCode(sourceFile);
        if (compileErrorMessage.length() > 0) {
            sourceFile.delete();
            return new Response(200, "", compileErrorMessage);
        }
        Response response = executeCode(parentDirectory);
        sourceFile.delete();
        return response;
    } catch (Exception e) {
        return new Response(502, "", e.toString());
    }
  }

  private static File loadCode(File sourceFile) throws IOException {
    JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
    DiagnosticCollector<JavaFileObject> diagnosticsCollector = new DiagnosticCollector<JavaFileObject>();

    StandardJavaFileManager fileManager = compiler.getStandardFileManager(null, null, null);

    File parentDirectory = sourceFile.getParentFile();
    fileManager.setLocation(StandardLocation.CLASS_OUTPUT, Arrays.asList(parentDirectory));

    Iterable<? extends JavaFileObject> compilationUnits = fileManager.getJavaFileObjectsFromFiles(Arrays.asList(sourceFile));
    boolean success = compiler.getTask(null, fileManager, diagnosticsCollector, null, null, compilationUnits).call();

    if (!success) {
        List<Diagnostic<? extends JavaFileObject>> diagnostics = diagnosticsCollector.getDiagnostics();
        for (Diagnostic<? extends JavaFileObject> diagnostic : diagnostics) {
            compileErrorMessage += diagnostic.getMessage(null);
        }
        return parentDirectory;
    }

    fileManager.close();
    return parentDirectory;
  }

  private static Response executeCode(File parentDirectory) {
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    ByteArrayOutputStream err = new ByteArrayOutputStream();

    PrintStream origOut = System.out;
    PrintStream origErr = System.err;

    System.setOut(new PrintStream(out));
    System.setErr(new PrintStream(err));

    try {
        URLClassLoader classLoader = URLClassLoader.newInstance(new URL[] { parentDirectory.toURI().toURL() });
        Class<?> main = classLoader.loadClass("Main");
        classLoader.close();

         Method mainMethod = main.getDeclaredMethod("main");
         mainMethod.invoke(main.newInstance());

    } catch (Exception e) {
      e.printStackTrace();
    }

    System.setOut(origOut);
    System.setErr(origErr);
    return new Response(200, out.toString(), err.toString());
  }

}