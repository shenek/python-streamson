use pyo3::prelude::*;
use streamson_lib::strategy;

use crate::{handler::BaseHandler, PythonOutput, PythonStrategy, RustMatcher};

/// Low level Python wrapper for Filter strategy
#[pyclass]
pub struct Filter {
    filter: strategy::Filter,
}

#[pymethods]
impl Filter {
    /// Create a new instance of Filter
    #[new]
    pub fn new() -> PyResult<Self> {
        let filter = strategy::Filter::new();
        Ok(Self { filter })
    }

    /// Adds matcher for Filter
    ///
    /// # Arguments
    /// * `matcher` - matcher to be added (`Simple`, `Depth`, ...)
    pub fn add_matcher(&mut self, matcher: &RustMatcher, handler: Option<BaseHandler>) {
        self.filter.add_matcher(
            Box::new(matcher.inner.clone()),
            if let Some(hndlr) = handler {
                Some(hndlr.inner.clone())
            } else {
                None
            },
        );
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

impl PythonStrategy<strategy::Filter> for Filter {
    fn get_strategy(&mut self) -> &mut strategy::Filter {
        &mut self.filter
    }
}
