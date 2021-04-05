use super::BaseHandler;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct RegexHandler {
    pub regex_inner: Arc<Mutex<handler::Regex>>,
}

#[pymethods]
impl RegexHandler {
    /// Create instance of Regex handler
    #[new]
    pub fn new(sedregexes: Vec<String>) -> (Self, BaseHandler) {
        let regex = sedregexes
            .into_iter()
            .fold(handler::Regex::new(), |regex, sed| regex.add_regex(sed));
        let regex_inner = Arc::new(Mutex::new(regex));
        (
            Self {
                regex_inner: regex_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(regex_inner))),
            },
        )
    }
}
