use pyo3::prelude::*;
use streamson_lib::strategy;

use crate::{handler::BaseHandler, PythonOutput, PythonStrategy, RustMatcher};

/// Low level Python wrapper for Extract strategy
#[pyclass]
pub struct Extract {
    extract: strategy::Extract,
}

#[pymethods]
impl Extract {
    /// Create a new instance of Extract
    ///
    /// # Arguments
    /// * `export_path` - indicator whether path is required in further processing
    #[new]
    pub fn new(export_path: Option<bool>) -> PyResult<Self> {
        let export_path = export_path.unwrap_or(true);
        let extract = strategy::Extract::new().set_export_path(export_path);
        Ok(Self { extract })
    }

    /// Adds matcher for Extract
    ///
    /// # Arguments
    /// * `matcher` - matcher to be added (`Simple`, `Depth`, ...)
    pub fn add_matcher(&mut self, matcher: &RustMatcher, handler: Option<BaseHandler>) {
        self.extract.add_matcher(
            Box::new(matcher.inner.clone()),
            if let Some(hndlr) = handler {
                Some(hndlr.inner)
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

impl PythonStrategy<strategy::Extract> for Extract {
    fn get_strategy(&mut self) -> &mut strategy::Extract {
        &mut self.extract
    }
}
