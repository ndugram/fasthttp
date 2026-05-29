use pyo3::prelude::*;
use std::collections::HashMap;
use std::collections::BTreeMap;

/// Build Cookie request header value from a name→value map.
/// Produces stable output by sorting keys alphabetically.
#[pyfunction]
pub fn build_cookie_header(cookies: HashMap<String, String>) -> String {
    let sorted: BTreeMap<_, _> = cookies.iter().collect();
    sorted
        .iter()
        .map(|(k, v)| format!("{}={}", k, v))
        .collect::<Vec<_>>()
        .join("; ")
}

/// Parse a raw Set-Cookie header value into {name: value}.
/// Matches Python's split(",") → split(";")[0] → split("=", 1) behavior.
#[pyfunction]
pub fn parse_set_cookie_header(raw: &str) -> HashMap<String, String> {
    let mut cookies = HashMap::new();
    for cookie_str in raw.split(',') {
        let name_value = match cookie_str.split(';').next() {
            Some(s) => s.trim(),
            None => continue,
        };
        if let Some(eq_pos) = name_value.find('=') {
            let name = name_value[..eq_pos].trim();
            let value = name_value[eq_pos + 1..].trim();
            if !name.is_empty() {
                cookies.insert(name.to_string(), value.to_string());
            }
        }
    }
    cookies
}
