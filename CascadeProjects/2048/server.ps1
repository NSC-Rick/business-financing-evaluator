# Simple HTTP server for 2048 game
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:8080/")
$listener.Start()

Write-Host "Server started at http://localhost:8080/"
Write-Host "Press Ctrl+C to stop the server"

try {
    while ($true) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $localPath = $request.Url.LocalPath
        if ($localPath -eq "/") {
            $localPath = "/index.html"
        }
        
        $filePath = Join-Path $PSScriptRoot $localPath.TrimStart('/')
        
        if (Test-Path $filePath -PathType Leaf) {
            $content = [System.IO.File]::ReadAllBytes($filePath)
            $response.ContentLength64 = $content.Length
            
            $extension = [System.IO.Path]::GetExtension($filePath)
            switch ($extension) {
                ".html" { $response.ContentType = "text/html" }
                ".css" { $response.ContentType = "text/css" }
                ".js" { $response.ContentType = "application/javascript" }
                default { $response.ContentType = "application/octet-stream" }
            }
            
            $response.OutputStream.Write($content, 0, $content.Length)
        } else {
            $response.StatusCode = 404
            $response.ContentType = "text/html"
            $message = "404 - File not found"
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($message)
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        
        $response.Close()
    }
} finally {
    $listener.Stop()
    Write-Host "Server stopped"
}
