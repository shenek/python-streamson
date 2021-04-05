use pyo3::prelude::*;
use streamson_lib::strategy;

use crate::{handler::BaseHandler, PythonOutput, PythonStrategy, RustMatcher};

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

    /// Adds matcher for Extract
    ///
    /// # Arguments
    /// * `matcher` - matcher to be added (`Simple`, `Depth`, ...)
    pub fn add_matcher(&mut self, matcher: &RustMatcher, handler: &BaseHandler) {
        self.trigger
            .add_matcher(Box::new(matcher.inner.clone()), handler.inner.clone());
    }

    /// Processes input data
    fn process(&mut self, input_data: &[u8]) -> PyResult<Vec<PythonOutput>> {
        self._process(input_data)
    }

    /// Functions which is triggered when the input has stopped
    fn terminate(&mut self) -> PyResult<Vec<PythonOutput>> {
        self._terminate()
    }
}

impl PythonStrategy<strategy::Trigger> for Trigger {
    fn get_strategy(&mut self) -> &mut strategy::Trigger {
        &mut self.trigger
    }
}
