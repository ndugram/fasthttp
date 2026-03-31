
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
            --bg-primary: #f4f4f4;
            --bg-secondary: #ffffff;
            --text-primary: #1e1e1e;
            --text-secondary: #9f9f9f;
            --border-color: #e0e0e0;
        }

        [data-theme="dark"] {
            --color-gray: #1a1a1a;
            --color-total-black: #f4f4f4;
            --color-text-gray: #9f9f9f;
            --bg-primary: #121212;
            --bg-secondary: #1e1e1e;
            --text-primary: #f4f4f4;
            --text-secondary: #9f9f9f;
            --border-color: #333333;
        }

        *, *::before, *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            background-color: var(--bg-primary);
            -webkit-text-size-adjust: 100%;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-urbanist), var(--font-manrope), system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            line-height: 1.5;
            transition: background-color 0.3s ease, color 0.3s ease;
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
            background: var(--bg-secondary);
            border-top-left-radius: 16px;
            border-bottom-left-radius: 28px;
            transform: skewX(-14deg);
            transform-origin: bottom left;
            z-index: 1;
            transition: background-color 0.3s ease;
        }

        .header-bg-right {
            position: absolute;
            top: 0;
            right: 0;
            width: 85%;
            height: 100%;
            background: var(--bg-secondary);
            border-radius: 16px;
            z-index: 0;
            transition: background-color 0.3s ease;
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
            color: var(--text-primary);
            transition: color 0.3s ease;
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
            color: var(--text-primary);
            text-decoration: none;
            background: rgba(46, 115, 255, 0.1);
            border-radius: 10px;
            transition: all 0.2s ease;
        }

        .nav a:hover {
            background: rgba(46, 115, 255, 0.2);
        }

        /* Theme Toggle */
        .theme-toggle {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: var(--bg-secondary);
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            z-index: 10;
        }

        .theme-toggle:hover {
            background: rgba(46, 115, 255, 0.1);
        }

        .theme-toggle svg {
            width: 20px;
            height: 20px;
            fill: var(--text-primary);
            transition: fill 0.3s ease;
        }

        .theme-toggle .sun-icon { display: none; }
        .theme-toggle .moon-icon { display: block; }

        [data-theme="dark"] .theme-toggle .sun-icon { display: block; }
        [data-theme="dark"] .theme-toggle .moon-icon { display: none; }

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
            background: var(--bg-secondary);
            border-radius: 24px;
            text-align: center;
            max-width: 600px;
            width: 100%;
            transition: background-color 0.3s ease;
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
            color: var(--text-primary);
            transition: color 0.3s ease;
        }

        .subtitle {
            color: var(--text-secondary);
            font-size: 16px;
            max-width: 400px;
            line-height: 1.5;
            margin-bottom: 32px;
            transition: color 0.3s ease;
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

        /* Footer */
        .footer {
            margin-top: auto;
            padding: 24px 0;
            width: 100%;
        }

        .footer-content {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
        }

        .footer-link {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            transition: all 0.2s ease;
            text-decoration: none;
        }

        .footer-link:hover {
            background: var(--color-brand-blue);
            color: var(--color-white);
            transform: translateY(-2px);
        }

        .footer-link svg {
            width: 22px;
            height: 22px;
        }
    </style>
    <script>
        (function() {
            const savedTheme = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const theme = savedTheme || (prefersDark ? 'dark' : 'light');
            if (theme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'dark');
            }

            window.toggleTheme = function() {
                const current = document.documentElement.getAttribute('data-theme');
                const next = current === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', next);
                localStorage.setItem('theme', next);
            };
        })();
    </script>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-bg-left"></div>
            <div class="header-bg-right"></div>
            <div class="logo">fast<span>http</span></div>
            <nav class="nav">
                <a href="__FASTHTTP_DOCS_URL__">__FASTHTTP_DOCS_URL__</a>
                <a href="__FASTHTTP_OPENAPI_URL__">__FASTHTTP_OPENAPI_URL__</a>
            </nav>
            <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">
                <svg class="moon-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
                </svg>
                <svg class="sun-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="5"/>
                    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                </svg>
            </button>
        </header>
    </div>

    <main>
        <div class="error-card">
            <div class="error-code">404</div>
            <h1>Page not found</h1>
            <p class="subtitle">The page you're looking for doesn't exist or has been moved.</p>
            <div class="links">
                <a href="__FASTHTTP_DOCS_URL__" class="btn btn-primary">GET __FASTHTTP_DOCS_URL__</a>
                <a href="__FASTHTTP_OPENAPI_URL__" class="btn btn-outline">GET __FASTHTTP_OPENAPI_URL__</a>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <a href="https://github.com/ndugram/fasthttp" class="footer-link" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                </svg>
            </a>
        </div>
    </footer>
</body>
</html>
"""


def get_not_found_html(*, docs_url: str = "/docs", openapi_url: str = "/openapi.json") -> str:
    return (
        NOT_FOUND_HTML
        .replace("__FASTHTTP_DOCS_URL__", docs_url)
        .replace("__FASTHTTP_OPENAPI_URL__", openapi_url)
    )


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
        .swagger-header {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 12px 20px;
            background: #fff;
            border-bottom: 1px solid #e0e0e0;
            gap: 12px;
        }
        .swagger-links {
            display: flex;
            gap: 8px;
            margin-right: auto;
        }
        .swagger-link {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: #f4f4f4;
            color: #1e1e1e;
            transition: all 0.2s ease;
            text-decoration: none;
        }
        .swagger-link:hover {
            background: #2e73ff;
            color: #fff;
        }
        .swagger-link svg {
            width: 18px;
            height: 18px;
            fill: currentColor;
        }
    </style>
</head>
<body>
    <div class="swagger-header">
        <div class="swagger-links">
            <a href="https://github.com/ndugram/fasthttp" class="swagger-link" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                </svg>
            </a>
        </div>
    </div>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" charset="UTF-8"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
    <script>
        let cachedSchema = null;

        async function initSwagger() {
            try {
                console.log('Fetching __FASTHTTP_OPENAPI_URL__...');
                const response = await fetch('__FASTHTTP_OPENAPI_URL__');
                console.log('Response status:', response.status);
                if (!response.ok) throw new Error('Failed to fetch schema: ' + response.status);

                const schema = await response.json();
                console.log('Schema loaded:', schema);
                cachedSchema = schema;

                schema.servers = [{ url: '__FASTHTTP_REQUEST_URL__', description: 'FastHTTP Proxy' }];

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

                        req.url = '__FASTHTTP_REQUEST_URL__';
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


def get_swagger_html(*, openapi_url: str = "/openapi.json", request_url: str = "/request") -> str:
    return (
        SWAGGER_HTML
        .replace("__FASTHTTP_OPENAPI_URL__", openapi_url)
        .replace("__FASTHTTP_REQUEST_URL__", request_url)
    )
