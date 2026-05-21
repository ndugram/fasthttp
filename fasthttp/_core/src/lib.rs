mod headers;
mod ip;
mod secrets;
mod url_utils;
mod xss;

use headers::{check_response_headers, sanitize_request_headers};
use ip::{is_local_hostname, is_private_ip};
use pyo3::prelude::*;
use secrets::{mask_cookie, mask_headers, mask_log_message, should_mask_value};
use url_utils::{apply_base_url, cache_key, check_https_url, extract_assets, join_prefix, resolve_url};
use xss::{detect_xss, sanitize_html};

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(check_https_url, m)?)?;
    m.add_function(wrap_pyfunction!(join_prefix, m)?)?;
    m.add_function(wrap_pyfunction!(resolve_url, m)?)?;
    m.add_function(wrap_pyfunction!(apply_base_url, m)?)?;
    m.add_function(wrap_pyfunction!(extract_assets, m)?)?;
    m.add_function(wrap_pyfunction!(cache_key, m)?)?;
    m.add_function(wrap_pyfunction!(mask_cookie, m)?)?;
    m.add_function(wrap_pyfunction!(mask_headers, m)?)?;
    m.add_function(wrap_pyfunction!(mask_log_message, m)?)?;
    m.add_function(wrap_pyfunction!(should_mask_value, m)?)?;
    m.add_function(wrap_pyfunction!(detect_xss, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_html, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_request_headers, m)?)?;
    m.add_function(wrap_pyfunction!(check_response_headers, m)?)?;
    m.add_function(wrap_pyfunction!(is_private_ip, m)?)?;
    m.add_function(wrap_pyfunction!(is_local_hostname, m)?)?;
    Ok(())
}
