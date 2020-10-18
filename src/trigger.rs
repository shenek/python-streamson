use super::{PythonHandler, RustMatcher, StreamsonError};
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::{handler, strategy};

/// Low level Python wrapper for Trigger strategy
#[pyclass]
pub struct Trigger {
    trigger: strategy::Trigger,
}

#[pymethods]
impl Trigger {
    /// Create a new instance of Trigger
    ///
    /// # Arguments
    /// * `export_path` - indicator whether path is required in further processing
    #[new]
    pub fn new() -> PyResult<Self> {
        let trigger = strategy::Trigger::new();
        Ok(Self { trigger })
    }

    /// Adds matcher for Trigger
    ///
    /// # Arguments
    /// * `matcher` - matcher to be added (`Simple` or `Depth`)
    pub fn add_matcher(&mut self, matcher: &RustMatcher, mut handlers: Vec<PythonHandler>) {
        let mut res: Vec<Arc<Mutex<dyn handler::Handler>>> = vec![];
        handlers
            .drain(..)
            .for_each(|e| res.push(Arc::new(Mutex::new(e))));
        self.trigger
            .add_matcher(Box::new(matcher.inner.clone()), &res);
    }

    pub fn process(&mut self, data: &[u8]) -> PyResult<String> {
        match self.trigger.process(data) {
            Err(err) => Err(StreamsonError::from(err).into()),
            Ok(()) => Ok(String::from_utf8(data.to_vec())?),
        }
    }
}
