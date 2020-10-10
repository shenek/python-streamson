use super::{RustMatcher, StreamsonError};
use pyo3::prelude::*;
use streamson_lib::strategy;

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
    /// * `matcher` - matcher to be added (`Simple` or `Depth`)
    pub fn add_matcher(&mut self, matcher: &RustMatcher) {
        self.filter.add_matcher(Box::new(matcher.inner.clone()));
    }

    /// Process data for Filter strategy
    ///
    /// # Arguments
    /// * `data` - input data to be processed
    ///
    /// # Returns
    /// * `filtered output`
    pub fn process(&mut self, data: &[u8]) -> PyResult<String> {
        match self.filter.process(data) {
            Err(err) => Err(StreamsonError::from(err).into()),
            Ok(data) => Ok(String::from_utf8(data)?),
        }
    }
}
