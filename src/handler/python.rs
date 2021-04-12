use super::{BaseHandler, PythonToken};
use pyo3::{prelude::*, types::PyBytes};
use std::{
    any::Any,
    sync::{Arc, Mutex},
};
use streamson_lib::{error, handler, path::Path, streamer};

/// Streamson handler which uses python callables to process
/// input and export output
#[derive(Clone)]
pub struct PythonInnerHandler {
    start_callable: PyObject,
    feed_callable: PyObject,
    end_callable: PyObject,
    require_path: bool,
    is_converter: bool,
}

impl PythonInnerHandler {
    pub fn new(
        start_callable: PyObject,
        feed_callable: PyObject,
        end_callable: PyObject,
        require_path: bool,
        is_converter: bool,
    ) -> Self {
        Self {
            start_callable,
            feed_callable,
            end_callable,
            require_path,
            is_converter,
        }
    }
}

impl handler::Handler for PythonInnerHandler {
    fn start(
        &mut self,
        path: &Path,
        matcher_idx: usize,
        token: streamer::Token,
    ) -> Result<Option<Vec<u8>>, error::Handler> {
        let gil = Python::acquire_gil();
        let py = gil.python();
        let res = self
            .start_callable
            .call1(
                py,
                (
                    if self.require_path {
                        Some(path.to_string())
                    } else {
                        None
                    },
                    matcher_idx,
                    PythonToken::from(token),
                ),
            )
            .map_err(|e| {
                error::Handler::new(format!("Failed to call start function: {}", e.to_string()))
            })?;
        if !res.is_none(py) {
            let bytes = res.cast_as::<PyBytes>(gil.python()).unwrap();
            FromPyObject::extract(bytes)
                .map_err(|_| error::Handler::new("Function does not return bytes."))
        } else {
            Ok(None)
        }
    }

    fn feed(&mut self, data: &[u8], matcher_idx: usize) -> Result<Option<Vec<u8>>, error::Handler> {
        let gil = Python::acquire_gil();
        let py = gil.python();
        let res = self
            .feed_callable
            .call1(py, (data.to_vec(), matcher_idx))
            .map_err(|e| {
                error::Handler::new(format!("Failed to call feed function: {}", e.to_string()))
            })?;
        if !res.is_none(py) {
            let bytes = res.cast_as::<PyBytes>(gil.python()).unwrap();
            FromPyObject::extract(bytes)
                .map_err(|_| error::Handler::new("Function does not return bytes."))
        } else {
            Ok(None)
        }
    }

    fn end(
        &mut self,
        path: &Path,
        matcher_idx: usize,
        token: streamer::Token,
    ) -> Result<Option<Vec<u8>>, error::Handler> {
        let gil = Python::acquire_gil();
        let py = gil.python();
        let res = self
            .end_callable
            .call1(
                py,
                (
                    if self.require_path {
                        Some(path.to_string())
                    } else {
                        None
                    },
                    matcher_idx,
                    PythonToken::from(token),
                ),
            )
            .map_err(|e| {
                error::Handler::new(format!("Failed to call end function: {}", e.to_string()))
            })?;
        if !res.is_none(py) {
            let bytes = res.cast_as::<PyBytes>(gil.python()).unwrap();
            FromPyObject::extract(bytes)
                .map_err(|_| error::Handler::new("Function does not return bytes."))
        } else {
            Ok(None)
        }
    }

    fn as_any(&self) -> &dyn Any {
        self
    }

    fn is_converter(&self) -> bool {
        true
    }
}

#[pyclass(extends=BaseHandler, subclass)]
#[derive(Clone)]
pub struct PythonHandler {
    pub python_inner: Arc<Mutex<PythonInnerHandler>>,
}

#[pymethods]
impl PythonHandler {
    /// Create instance of Python handler
    ///
    /// # Arguments
    /// * `start_callable` - python callable (3 arguments)
    /// * `feed_callable` - python callable (2 arguments)
    /// * `end_callable` - python callable (3 arguments)
    /// * `require_path` - should path be passed to handler
    #[new]
    pub fn new(
        start_callable: PyObject,
        feed_callable: PyObject,
        end_callable: PyObject,
        require_path: bool,
        is_converter: bool,
    ) -> (Self, BaseHandler) {
        let python_inner = Arc::new(Mutex::new(PythonInnerHandler::new(
            start_callable,
            feed_callable,
            end_callable,
            require_path,
            is_converter,
        )));
        (
            Self {
                python_inner: python_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(python_inner))),
            },
        )
    }
}
