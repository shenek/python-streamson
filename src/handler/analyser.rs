use super::BaseHandler;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct AnalyserHandler {
    pub analyser_inner: Arc<Mutex<handler::Analyser>>,
}

#[pymethods]
impl AnalyserHandler {
    /// Create instance of Analyser handler
    #[new]
    pub fn new() -> (Self, BaseHandler) {
        let analyser_inner = Arc::new(Mutex::new(handler::Analyser::new()));
        (
            Self {
                analyser_inner: analyser_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(
                    handler::Group::new().add_handler(analyser_inner),
                )),
            },
        )
    }

    /// Results of analysis
    pub fn results(&self) -> Vec<(String, usize)> {
        self.analyser_inner.lock().unwrap().results()
    }
}
