use pyo3::prelude::*;
use streamson_lib::strategy;

use crate::{handler::BaseHandler, PythonOutput, PythonStrategy, RustMatcher};

/// Low level Python wrapper for Convert strategy
#[pyclass]
pub struct Convert {
    convert: strategy::Convert,
}

#[pymethods]
impl Convert {
    /// Create a new instance of Convert
    ///
    /// # Arguments
    /// * `export_path` - indicator whether path is required in further processing
    #[new]
    pub fn new() -> PyResult<Self> {
        let convert = strategy::Convert::new();
        Ok(Self { convert })
    }

    /// Adds matcher for Convert
    ///
    /// # Arguments
    /// * `matcher` - matcher to be added (`Simple`, `Depth`, ...)
    /// * `handlers` - list of handlers to process
    pub fn add_matcher(&mut self, matcher: &RustMatcher, handler: &BaseHandler) {
        self.convert
            .add_matcher(Box::new(matcher.inner.clone()), handler.inner.clone())
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

impl PythonStrategy<strategy::Convert> for Convert {
    fn get_strategy(&mut self) -> &mut strategy::Convert {
        &mut self.convert
    }
}
