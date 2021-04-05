use super::BaseHandler;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct ShortenHandler {
    pub shorten_inner: Arc<Mutex<handler::Shorten>>,
}

#[pymethods]
impl ShortenHandler {
    /// Create instance of Shorten handler
    #[new]
    pub fn new(max_length: usize, terminator: String) -> (Self, BaseHandler) {
        let shorten_inner = Arc::new(Mutex::new(handler::Shorten::new(max_length, terminator)));
        (
            Self {
                shorten_inner: shorten_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(shorten_inner))),
            },
        )
    }
}
