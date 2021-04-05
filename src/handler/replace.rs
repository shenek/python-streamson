use super::BaseHandler;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct ReplaceHandler {
    pub replace_inner: Arc<Mutex<handler::Replace>>,
}

#[pymethods]
impl ReplaceHandler {
    /// Create instance of Regex handler
    #[new]
    pub fn new(new_data: String) -> (Self, BaseHandler) {
        let replace_inner = Arc::new(Mutex::new(handler::Replace::new(new_data.into_bytes())));
        (
            Self {
                replace_inner: replace_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(replace_inner))),
            },
        )
    }
}
