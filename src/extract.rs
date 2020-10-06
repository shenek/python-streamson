use super::{RustMatcher, StreamsonError};
use pyo3::prelude::*;
use streamson_lib::strategy;

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
    /// * `matcher` - matcher to be added (`Simple` or `Depth`)
    pub fn add_matcher(&mut self, matcher: &RustMatcher) {
        self.extract.add_matcher(Box::new(matcher.inner.clone()));
    }

    /// Process data for Extract strategy
    ///
    /// # Arguments
    /// * `data` - input data to be processed
    ///
    /// # Returns
    /// * `vector of tuples` - (path_or_none, data)
    pub fn process(&mut self, data: &[u8]) -> PyResult<Vec<(Option<String>, String)>> {
        match self.extract.process(data) {
            Err(err) => Err(StreamsonError::from(err).into()),
            Ok(chunks) => {
                let mut res = vec![];
                for (path, data) in chunks {
                    res.push((path, String::from_utf8(data)?));
                }
                Ok(res)
            }
        }
    }
}
