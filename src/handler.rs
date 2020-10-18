use pyo3::{prelude::*, types::PyBytes};
use streamson_lib::{error, handler, path::Path};

/// Streamson handler which performs data conversion
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

/// Streamson handler which calls python callable
#[pyclass]
#[derive(Clone)]
pub struct PythonHandler {
    callable: PyObject,
    require_path: bool,
}

#[pymethods]
impl PythonHandler {
    /// Create instance of PythonHandler
    ///
    /// # Arguments
    /// * `callable` - python callable (3 arguments)
    /// * `require_path` - should path be passed to handler
    #[new]
    pub fn new(callable: PyObject, require_path: bool) -> Self {
        Self {
            callable,
            require_path,
        }
    }
}

impl handler::Handler for PythonHandler {
    /// Call python function as a part of rust handler
    ///
    /// # Arguments
    /// * `path` - matched path
    /// * `matcher_idx` - index of triggered matcher
    /// * `data` - matched data
    fn handle(
        &mut self,
        path: &Path,
        matcher_idx: usize,
        data: Option<&[u8]>,
    ) -> Result<Option<Vec<u8>>, error::Handler> {
        let gil = Python::acquire_gil();
        self.callable
            .call1(
                gil.python(),
                (
                    if self.require_path {
                        Some(path.to_string())
                    } else {
                        None
                    },
                    matcher_idx,
                    data,
                ),
            )
            .map_err(|_| error::Handler::new("Calling python failed"))?;
        Ok(None)
    }
}
