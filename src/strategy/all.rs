use pyo3::prelude::*;
use streamson_lib::strategy;

use crate::{handler::BaseHandler, PythonOutput, PythonStrategy};

/// Low level Python wrapper for All strategy
#[pyclass]
pub struct All {
    all: strategy::All,
}

#[pymethods]
impl All {
    /// Create a new instance of All
    ///
    /// # Arguments
    /// * `convert` - should handler be used for output conversion
    #[new]
    #[args(convert = "None")]
    pub fn new(convert: Option<bool>) -> PyResult<Self> {
        let convert = convert.unwrap_or(false);
        let mut all = strategy::All::new();
        all.set_convert(convert);
        Ok(Self { all })
    }

    /// Adds handler for all strategy
    ///
    /// # Arguments
    /// * `handler` - handler to be added (`Indent`, `Analyser`, ...)
    pub fn add_handler(&mut self, handler: BaseHandler) {
        self.all.add_handler(handler.inner);
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

impl PythonStrategy<strategy::All> for All {
    fn get_strategy(&mut self) -> &mut strategy::All {
        &mut self.all
    }
}
