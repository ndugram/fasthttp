use once_cell::sync::Lazy;
use pyo3::prelude::*;
use regex::Regex;

static XSS_SCRIPT_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)<script[^>]*>").unwrap());
static XSS_JS_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)javascript:").unwrap());
static XSS_ONHANDLER_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)on\w+\s*=").unwrap());
static XSS_IFRAME_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)<iframe[^>]*>").unwrap());
static XSS_OBJECT_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)<object[^>]*>").unwrap());
static XSS_EMBED_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)<embed[^>]*>").unwrap());
static XSS_APPLET_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)<applet[^>]*>").unwrap());
static XSS_VBSCRIPT_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)vbscript:").unwrap());
static XSS_DATA_HTML_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)data:text/html").unwrap());
static XSS_EVENT_HANDLER_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r#"(?i)\s+on\w+\s*=\s*["']"#).unwrap());
static HTML_TAG_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"<[^>]+>").unwrap());
static SCRIPT_TAG_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?is)<script[^>]*>.*?</script>").unwrap());

/// Scan content for XSS patterns. Returns (found: bool, reason: str | None).
#[pyfunction]
pub fn detect_xss(content: &str) -> (bool, Option<String>) {
    if XSS_SCRIPT_RE.is_match(content)
        || XSS_JS_RE.is_match(content)
        || XSS_ONHANDLER_RE.is_match(content)
        || XSS_IFRAME_RE.is_match(content)
        || XSS_OBJECT_RE.is_match(content)
        || XSS_EMBED_RE.is_match(content)
        || XSS_APPLET_RE.is_match(content)
        || XSS_VBSCRIPT_RE.is_match(content)
        || XSS_DATA_HTML_RE.is_match(content)
    {
        return (true, Some("Potential XSS detected in response".to_string()));
    }
    if XSS_EVENT_HANDLER_RE.is_match(content) {
        return (
            true,
            Some("Potential XSS (event handler) detected in response".to_string()),
        );
    }
    (false, None)
}

/// Strip script tags and all HTML tags from content.
#[pyfunction]
pub fn sanitize_html(content: &str) -> String {
    let r = SCRIPT_TAG_RE.replace_all(content, "");
    let r = HTML_TAG_RE.replace_all(r.as_ref(), "");
    r.into_owned()
}
