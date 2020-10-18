use super::{PythonConverter, RustMatcher, StreamsonError};
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::{handler, strategy};

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
    /// * `matcher` - matcher to be added (`Simple` or `Depth`)
    /// * `handlers` - list of handlers to process
    pub fn add_matcher(&mut self, matcher: &RustMatcher, mut handlers: Vec<PythonConverter>) {
        let mut res: Vec<Arc<Mutex<dyn handler::Handler>>> = vec![];
        handlers
            .drain(..)
            .for_each(|e| res.push(Arc::new(Mutex::new(e))));

        self.convert
            .add_matcher(Box::new(matcher.inner.clone()), res)
    }

    pub fn process(&mut self, input_data: &[u8]) -> PyResult<String> {
        match self.convert.process(input_data) {
            Err(err) => Err(StreamsonError::from(err).into()),
            Ok(data_list) => {
                let mut res = String::new();
                for out_data in data_list {
                    res += &String::from_utf8(out_data.to_vec())?;
                }
                Ok(res)
            }
        }
    }
}
