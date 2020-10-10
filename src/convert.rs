use super::{RustMatcher, StreamsonError};
use pyo3::{prelude::*, types::PyBytes};
use std::sync::{Arc, Mutex};
use streamson_lib::{error, handler, path::Path, strategy};

/// TODO
#[pyclass]
#[derive(Clone)]
pub struct PythonConverter {
    callable: PyObject,
    use_path: bool,
}

#[pymethods]
impl PythonConverter {
    /// Create instance of PythonConverter
    ///
    /// # Arguments
    /// * `callable` - python callable (3 arguments)
    #[new]
    pub fn new(callable: PyObject, use_path: bool) -> Self {
        Self { callable, use_path }
    }
}

impl handler::Handler for PythonConverter {
    fn handle(
        &mut self,
        path: &Path,
        matcher_idx: usize,
        data: Option<&[u8]>,
    ) -> Result<Option<Vec<u8>>, error::Handler> {
        let gil = Python::acquire_gil();
        let res = self
            .callable
            .call1(
                gil.python(),
                (
                    if self.use_path {
                        Some(path.to_string())
                    } else {
                        None
                    },
                    matcher_idx,
                    data.unwrap().to_vec(),
                ),
            )
            .map_err(|_| error::Handler::new("Failed to call handler function"))?;
        let bytes = res.cast_as::<PyBytes>(gil.python()).unwrap();
        Ok(FromPyObject::extract(bytes)
            .map_err(|_| error::Handler::new("Function does not return bytes."))?)
    }
}

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
