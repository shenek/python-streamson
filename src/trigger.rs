use super::{RustMatcher, StreamsonError};
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::{error, handler, path::Path, strategy};

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
    ) -> Result<(), error::Handler> {
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
        Ok(())
    }
}

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

    /// Adds matcher for Trigger
    ///
    /// # Arguments
    /// * `matcher` - matcher to be added (`Simple` or `Depth`)
    pub fn add_matcher(&mut self, matcher: &RustMatcher, mut handlers: Vec<PythonHandler>) {
        let mut res: Vec<Arc<Mutex<dyn handler::Handler>>> = vec![];
        handlers
            .drain(..)
            .for_each(|e| res.push(Arc::new(Mutex::new(e))));
        self.trigger
            .add_matcher(Box::new(matcher.inner.clone()), &res);
    }

    pub fn process(&mut self, data: &[u8]) -> PyResult<String> {
        match self.trigger.process(data) {
            Err(err) => Err(StreamsonError::from(err).into()),
            Ok(()) => Ok(String::from_utf8(data.to_vec())?),
        }
    }
}
