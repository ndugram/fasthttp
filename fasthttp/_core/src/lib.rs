mod cookies;
mod headers;
mod ip;
mod redirect;
mod response_check;
mod secrets;
mod signer;
mod url_utils;
mod xss;

use cookies::{build_cookie_header, parse_set_cookie_header};
use headers::{check_response_headers, sanitize_request_headers};
use ip::{is_local_hostname, is_private_ip};
use pyo3::prelude::*;
use redirect::check_redirect_url;
use response_check::{check_content_type, check_response_size, validate_response};
use secrets::{mask_cookie, mask_headers, mask_log_message, mask_url, should_mask_value};
use signer::{sign_request, verify_request};
use url_utils::{apply_base_url, cache_key, check_https_url, detect_path_traversal, extract_assets, join_prefix, normalize_url_for_matching, resolve_url};
use xss::{detect_xss, sanitize_html};

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // url utils
    m.add_function(wrap_pyfunction!(check_https_url, m)?)?;
    m.add_function(wrap_pyfunction!(join_prefix, m)?)?;
    m.add_function(wrap_pyfunction!(resolve_url, m)?)?;
    m.add_function(wrap_pyfunction!(apply_base_url, m)?)?;
    m.add_function(wrap_pyfunction!(extract_assets, m)?)?;
    m.add_function(wrap_pyfunction!(cache_key, m)?)?;
    // secrets masking
    m.add_function(wrap_pyfunction!(mask_cookie, m)?)?;
    m.add_function(wrap_pyfunction!(mask_headers, m)?)?;
    m.add_function(wrap_pyfunction!(mask_log_message, m)?)?;
    m.add_function(wrap_pyfunction!(should_mask_value, m)?)?;
    m.add_function(wrap_pyfunction!(mask_url, m)?)?;
    // xss
    m.add_function(wrap_pyfunction!(detect_xss, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_html, m)?)?;
    // headers
    m.add_function(wrap_pyfunction!(sanitize_request_headers, m)?)?;
    m.add_function(wrap_pyfunction!(check_response_headers, m)?)?;
    // ip
    m.add_function(wrap_pyfunction!(is_private_ip, m)?)?;
    m.add_function(wrap_pyfunction!(is_local_hostname, m)?)?;
    // signer
    m.add_function(wrap_pyfunction!(sign_request, m)?)?;
    m.add_function(wrap_pyfunction!(verify_request, m)?)?;
    // cookies
    m.add_function(wrap_pyfunction!(build_cookie_header, m)?)?;
    m.add_function(wrap_pyfunction!(parse_set_cookie_header, m)?)?;
    // response validation
    m.add_function(wrap_pyfunction!(check_response_size, m)?)?;
    m.add_function(wrap_pyfunction!(check_content_type, m)?)?;
    m.add_function(wrap_pyfunction!(validate_response, m)?)?;
    // redirect
    m.add_function(wrap_pyfunction!(check_redirect_url, m)?)?;
    // path / url utils
    m.add_function(wrap_pyfunction!(detect_path_traversal, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_url_for_matching, m)?)?;
    Ok(())
}
