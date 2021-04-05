use super::BaseHandler;
use crate::handler::PythonToken;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct IndexerHandler {
    pub indexer_inner: Arc<Mutex<handler::Indexer>>,
}

#[pymethods]
impl IndexerHandler {
    /// Create instance of Indexer handler
    #[new]
    #[args(use_path = "true")]
    pub fn new(use_path: bool) -> (Self, BaseHandler) {
        let indexer_inner = Arc::new(Mutex::new(handler::Indexer::new().set_use_path(use_path)));
        (
            Self {
                indexer_inner: indexer_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(indexer_inner))),
            },
        )
    }

    /// Remove first element from the buffer
    pub fn pop_front(&mut self) -> Option<(Option<String>, PythonToken)> {
        self.indexer_inner
            .lock()
            .unwrap()
            .pop()
            .map(|(path, token)| (path, token.into()))
    }
}
