
NOT_FOUND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 — FastHTTP</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Urbanist:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --font-urbanist: 'Urbanist', system-ui, sans-serif;
            --font-manrope: 'Manrope', system-ui, sans-serif;
            --color-brand-green: #30fc9d;
            --color-brand-blue: #2e73ff;
            --color-total-black: #1e1e1e;
            --color-text-gray: #9f9f9f;
            --color-gray: #f4f4f4;
            --color-white: #ffffff;
        }

        *, *::before, *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            background-color: var(--color-gray);
            -webkit-text-size-adjust: 100%;
        }

        body {
            background-color: var(--color-gray);
            color: var(--color-total-black);
            font-family: var(--font-urbanist), var(--font-manrope), system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            line-height: 1.5;
        }

        .container {
            width: 100%;
            max-width: 1408px;
            padding: 0 20px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px 12px 12px;
            height: 56px;
            border-radius: 16px;
            overflow: hidden;
            margin: 20px auto;
            max-width: calc(1408px - 40px);
            width: calc(100% - 40px);
        }

        .header-bg-left {
            position: absolute;
            top: 0;
            left: 0;
            width: 35%;
            height: 100%;
            background: var(--color-white);
            border-top-left-radius: 16px;
            border-bottom-left-radius: 28px;
            transform: skewX(-14deg);
            transform-origin: bottom left;
            z-index: 1;
        }

        .header-bg-right {
            position: absolute;
            top: 0;
            right: 0;
            width: 85%;
            height: 100%;
            background: var(--color-white);
            border-radius: 16px;
            z-index: 0;
        }

        .logo {
            display: inline-flex;
            align-items: center;
            gap: 0;
            position: relative;
            z-index: 10;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        .logo span {
            color: var(--color-brand-blue);
        }

        .nav {
            display: flex;
            align-items: center;
            gap: 16px;
            position: relative;
            z-index: 10;
        }

        .nav a {
            display: inline-flex;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            color: var(--color-total-black);
            text-decoration: none;
            background: rgba(46, 115, 255, 0.1);
            border-radius: 10px;
            transition: all 0.2s ease;
        }

        .nav a:hover {
            background: rgba(46, 115, 255, 0.2);
        }

        /* Main */
        main {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            padding: 20px;
        }

        .error-card {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px 40px;
            background: var(--color-white);
            border-radius: 24px;
            text-align: center;
            max-width: 600px;
            width: 100%;
        }

        .error-code {
            font-family: var(--font-urbanist);
            font-size: clamp(80px, 15vw, 140px);
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.04em;
            color: var(--color-brand-blue);
            margin-bottom: 16px;
        }

        h1 {
            font-family: var(--font-urbanist);
            font-size: clamp(24px, 4vw, 36px);
            font-weight: 600;
            letter-spacing: -0.02em;
            line-height: 1.1;
            margin-bottom: 12px;
        }

        .subtitle {
            color: var(--color-text-gray);
            font-size: 16px;
            max-width: 400px;
            line-height: 1.5;
            margin-bottom: 32px;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            white-space: nowrap;
            transition: all 0.2s ease;
            text-decoration: none;
            border: none;
            cursor: pointer;
        }

        .btn-primary {
            background: var(--color-brand-blue);
            color: var(--color-white);
        }

        .btn-primary:hover {
            background: #1f5fd9;
        }

        .btn-outline {
            background: transparent;
            color: var(--color-brand-blue);
            border: 2px solid var(--color-brand-blue);
        }

        .btn-outline:hover {
            background: rgba(46, 115, 255, 0.1);
        }

        .links {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: center;
        }

        @media (max-width: 640px) {
            .nav {
                display: none;
            }

            .error-card {
                padding: 40px 24px;
            }

            .links {
                flex-direction: column;
                width: 100%;
            }

            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-bg-left"></div>
            <div class="header-bg-right"></div>
            <div class="logo">fast<span>http</span></div>
            <nav class="nav">
                <a href="/docs">/docs</a>
                <a href="/openapi.json">/openapi.json</a>
            </nav>
        </header>
    </div>

    <main>
        <div class="error-card">
            <div class="error-code">404</div>
            <h1>Page not found</h1>
            <p class="subtitle">The page you're looking for doesn't exist or has been moved.</p>
            <div class="links">
                <a href="/docs" class="btn btn-primary">GET /docs</a>
                <a href="/openapi.json" class="btn btn-outline">GET /openapi.json</a>
            </div>
        </div>
    </main>
</body>
</html>
"""


def get_not_found_html() -> str:
    return NOT_FOUND_HTML


SWAGGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastHTTP API Docs</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui.css">
    <style>
        body { margin: 0; padding: 0; }
        .topbar { display: none; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" charset="UTF-8"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
    <script>
        let cachedSchema = null;

        async function initSwagger() {
            try {
                console.log('Fetching /openapi.json...');
                const response = await fetch('/openapi.json');
                console.log('Response status:', response.status);
                if (!response.ok) throw new Error('Failed to fetch schema: ' + response.status);

                const schema = await response.json();
                console.log('Schema loaded:', schema);
                cachedSchema = schema;

                schema.servers = [{ url: '/request', description: 'FastHTTP Proxy' }];

                const ui = SwaggerUIBundle({
                    spec: schema,
                    dom_id: "#swagger-ui",
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    layout: "StandaloneLayout",
                    requestInterceptor: function(req) {
                        let method = (req.method || 'GET').toUpperCase();
                        let operationPath = null;
                        let originalUrl = null;

                        if (cachedSchema && cachedSchema.paths && req.operationId) {
                            for (const path in cachedSchema.paths) {
                                const pathItem = cachedSchema.paths[path];
                                for (const httpMethod in pathItem) {
                                    if (pathItem[httpMethod] && pathItem[httpMethod].operationId === req.operationId) {
                                        operationPath = path;
                                        const op = pathItem[httpMethod];
                                        originalUrl = op['x-original-url'];
                                        break;
                                    }
                                }
                                if (originalUrl) break;
                            }
                        }

                        if (!originalUrl && cachedSchema && cachedSchema.paths) {
                            // req.url is the full URL including server, extract path part
                            for (const path in cachedSchema.paths) {
                                if (req.url.includes(path)) {
                                    const pathItem = cachedSchema.paths[path];
                                    if (pathItem[method.toLowerCase()]) {
                                        originalUrl = pathItem[method.toLowerCase()]['x-original-url'];
                                        break;
                                    }
                                }
                            }
                        }

                        let body = null;
                        if (req.body) {
                            try {
                                body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
                            } catch (e) { body = req.body; }
                        }

                        req.url = '/request';
                        req.method = 'POST';
                        req.body = JSON.stringify({
                            url: originalUrl,
                            method: method,
                            headers: req.headers,
                            body: body
                        });
                        req.headers['Content-Type'] = 'application/json';

                        return req;
                    },
                    responseInterceptor: function(resp) {
                        try {
                            const data = JSON.parse(resp.text);
                            if (data.status !== undefined) {
                                resp.status = data.status;
                                resp.text = data.body || '';
                                resp.headers = data.headers || {};
                            }
                        } catch (e) {}
                        return resp;
                    }
                });

                window.ui = ui;
            } catch (err) {
                console.error('Error:', err);
                const errorMsg = err.message + '\\n\\nCheck console (F12) for details.';
                document.getElementById('swagger-ui').innerHTML =
                    '<pre style="color:red; padding:20px;">Error: ' + errorMsg + '</pre>';
            }
        }

        initSwagger();
    </script>
</body>
</html>
"""


def get_swagger_html() -> str:
    return SWAGGER_HTML
