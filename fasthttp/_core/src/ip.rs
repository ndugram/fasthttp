use once_cell::sync::Lazy;
use pyo3::prelude::*;
use std::collections::HashSet;
use std::net::{IpAddr, Ipv6Addr};

struct Ipv4Network {
    addr: u32,
    mask: u32,
}

impl Ipv4Network {
    const fn new(a: u8, b: u8, c: u8, d: u8, prefix: u8) -> Self {
        let addr = u32::from_be_bytes([a, b, c, d]);
        let mask = if prefix == 0 { 0 } else { !0u32 << (32 - prefix as u32) };
        Self { addr: addr & mask, mask }
    }

    #[inline]
    fn contains(&self, ip: u32) -> bool {
        (ip & self.mask) == self.addr
    }
}

// Full private range table — union of ssrf.py + redirect.py lists.
const PRIVATE_IPV4_NETS: &[Ipv4Network] = &[
    Ipv4Network::new(10, 0, 0, 0, 8),        // 10.0.0.0/8       RFC1918
    Ipv4Network::new(172, 16, 0, 0, 12),      // 172.16.0.0/12    RFC1918
    Ipv4Network::new(192, 168, 0, 0, 16),     // 192.168.0.0/16   RFC1918
    Ipv4Network::new(127, 0, 0, 0, 8),        // 127.0.0.0/8      loopback
    Ipv4Network::new(169, 254, 0, 0, 16),     // 169.254.0.0/16   link-local
    Ipv4Network::new(0, 0, 0, 0, 8),          // 0.0.0.0/8
    Ipv4Network::new(100, 64, 0, 0, 10),      // 100.64.0.0/10    shared (RFC6598)
    Ipv4Network::new(192, 0, 0, 0, 24),       // 192.0.0.0/24     IETF protocol
    Ipv4Network::new(192, 0, 2, 0, 24),       // 192.0.2.0/24     TEST-NET-1
    Ipv4Network::new(198, 51, 100, 0, 24),    // 198.51.100.0/24  TEST-NET-2
    Ipv4Network::new(203, 0, 113, 0, 24),     // 203.0.113.0/24   TEST-NET-3
    Ipv4Network::new(224, 0, 0, 0, 4),        // 224.0.0.0/4      multicast
    Ipv4Network::new(240, 0, 0, 0, 4),        // 240.0.0.0/4      reserved
];

#[inline]
fn is_ipv6_link_local(ip: &Ipv6Addr) -> bool {
    let b = ip.octets();
    b[0] == 0xfe && (b[1] & 0xc0) == 0x80
}

/// Return True if ip_str is private/loopback/link-local/multicast/reserved.
/// Accepts IPv4 and IPv6. Returns False for invalid input.
#[pyfunction]
pub fn is_private_ip(ip_str: &str) -> bool {
    match ip_str.trim().parse::<IpAddr>() {
        Ok(IpAddr::V4(v4)) => {
            let n = u32::from(v4);
            PRIVATE_IPV4_NETS.iter().any(|net| net.contains(n))
        }
        Ok(IpAddr::V6(v6)) => {
            v6.is_loopback() || v6.is_multicast() || is_ipv6_link_local(&v6)
        }
        Err(_) => false,
    }
}

static LOCAL_HOSTNAME_EXACT: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    HashSet::from([
        "localho.st",
        "lvh.me",
        "0x7f000001",
        "127.1",
        "::1",
        "0:0:0:0:0:0:0:1",
        "127.0.0.1",
        "0.0.0.0",
        "0",
    ])
});

// Checked with ends_with — matches Python's exact behaviour.
const LOCAL_DOMAIN_SUFFIXES: &[&str] = &[
    "localhost",
    "localhost.localdomain",
    "local",
    "intranet",
    "internal",
    "private",
];

/// Return True if hostname should be treated as local/internal without DNS lookup.
#[pyfunction]
pub fn is_local_hostname(hostname: &str) -> bool {
    let lower = hostname.trim().to_lowercase();
    if LOCAL_HOSTNAME_EXACT.contains(lower.as_str()) {
        return true;
    }
    LOCAL_DOMAIN_SUFFIXES.iter().any(|d| lower.ends_with(d))
}
