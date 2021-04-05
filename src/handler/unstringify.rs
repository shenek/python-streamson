use super::BaseHandler;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct UnstringifyHandler {
    pub unstringify_inner: Arc<Mutex<handler::Unstringify>>,
}

#[pymethods]
impl UnstringifyHandler {
    /// Create instance of Unstringify handler
    #[new]
    pub fn new() -> (Self, BaseHandler) {
        let unstringify_inner = Arc::new(Mutex::new(handler::Unstringify::new()));
        (
            Self {
                unstringify_inner: unstringify_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(
                    handler::Group::new().add_handler(unstringify_inner),
                )),
            },
        )
    }
}
