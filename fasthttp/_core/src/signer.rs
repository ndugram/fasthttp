use hmac::{Hmac, Mac};
use pyo3::prelude::*;
use rand::RngCore;
use sha2::Sha256;
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

type HmacSha256 = Hmac<Sha256>;

fn now_secs() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

fn bytes_to_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

fn hex_decode(s: &str) -> Option<Vec<u8>> {
    if s.len() % 2 != 0 {
        return None;
    }
    (0..s.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&s[i..i + 2], 16).ok())
        .collect()
}

fn build_payload(method: &str, url: &str, timestamp: u64, body: &[u8]) -> Vec<u8> {
    let body_str = std::str::from_utf8(body).unwrap_or("");
    format!("{}\n{}\n{}\n{}", method, url, timestamp, body_str).into_bytes()
}

/// Sign a request with HMAC-SHA256.
/// Returns {"X-Signature": hex_sig, "X-Timestamp": str(ts), "X-Nonce": hex_nonce(16 bytes)}.
#[pyfunction]
pub fn sign_request(
    secret_key: &[u8],
    method: &str,
    url: &str,
    body: &[u8],
) -> PyResult<HashMap<String, String>> {
    let timestamp = now_secs();

    let mut nonce_bytes = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = bytes_to_hex(&nonce_bytes);

    let payload = build_payload(method, url, timestamp, body);

    let mut mac = HmacSha256::new_from_slice(secret_key)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    mac.update(&payload);
    let signature = bytes_to_hex(&mac.finalize().into_bytes());

    let mut result = HashMap::new();
    result.insert("X-Signature".to_string(), signature);
    result.insert("X-Timestamp".to_string(), timestamp.to_string());
    result.insert("X-Nonce".to_string(), nonce);
    Ok(result)
}

/// Verify a request signature. True if valid and not expired (within max_age seconds).
#[pyfunction]
pub fn verify_request(
    secret_key: &[u8],
    method: &str,
    url: &str,
    timestamp: u64,
    body: &[u8],
    signature: &str,
    max_age: u64,
) -> bool {
    let now = now_secs();
    if now.abs_diff(timestamp) > max_age {
        return false;
    }

    let payload = build_payload(method, url, timestamp, body);

    let mut mac = match HmacSha256::new_from_slice(secret_key) {
        Ok(m) => m,
        Err(_) => return false,
    };
    mac.update(&payload);

    match hex_decode(signature) {
        Some(sig_bytes) => mac.verify_slice(&sig_bytes).is_ok(),
        None => false,
    }
}
