use super::BaseHandler;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct IndenterHandler {
    pub indenter_inner: Arc<Mutex<handler::Indenter>>,
}

#[pymethods]
impl IndenterHandler {
    /// Create instance of Indenter handler
    #[new]
    #[args(max_size = "Some(4)")]
    pub fn new(spaces: Option<usize>) -> (Self, BaseHandler) {
        let indenter_inner = Arc::new(Mutex::new(handler::Indenter::new(spaces)));
        (
            Self {
                indenter_inner: indenter_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(
                    handler::Group::new().add_handler(indenter_inner),
                )),
            },
        )
    }
}
