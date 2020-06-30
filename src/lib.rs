use pyo3::create_exception;
use pyo3::exceptions;
use pyo3::prelude::*;

use std::sync::{Arc, Mutex};
use streamson_lib::{error, handler, matcher, Collector};

create_exception!(streamson, StreamsonError, exceptions::ValueError);
create_exception!(streamson, MatcherUsed, exceptions::RuntimeError);

impl From<error::General> for StreamsonError {
    fn from(_gerror: error::General) -> Self {
        Self
    }
}

/// Python wrapper around matchers
#[pyclass]
#[derive(Debug)]
pub struct RustMatcher {
    inner: Option<matcher::Combinator>,
}

#[pymethods]
impl RustMatcher {
    /// Create a new instance of simple matcher
    ///
    /// # Arguments
    /// * `path` - path to match
    /// * `max_depth` - max depth
    #[staticmethod]
    pub fn simple(path: String) -> PyResult<Self> {
        Ok(Self {
            inner: Some(matcher::Combinator::new(matcher::Simple::new(path))),
        })
    }

    /// Create a new instance of depth matcher
    ///
    /// # Arguments
    /// * `min_depth` - min depth
    /// * `max_depth` - max depth (Optional)
    #[staticmethod]
    pub fn depth(min_depth: usize, max_depth: Option<usize>) -> PyResult<Self> {
        Ok(Self {
            inner: Some(matcher::Combinator::new(matcher::Depth::new(
                min_depth, max_depth,
            ))),
        })
    }

    pub fn inv(&mut self) -> PyResult<Self> {
        if let Some(inner) = self.inner.take() {
            Ok(Self {
                inner: Some(!inner),
            })
        } else {
            Err(MatcherUsed.into())
        }
    }

    pub fn any(&mut self, right: &mut RustMatcher) -> PyResult<Self> {
        if let (Some(left), Some(right)) = (self.inner.take(), right.inner.take()) {
            Ok(Self {
                inner: Some(left | right),
            })
        } else {
            Err(MatcherUsed.into())
        }
    }

    pub fn all(&mut self, right: &mut RustMatcher) -> PyResult<Self> {
        if let (Some(left), Some(right)) = (self.inner.take(), right.inner.take()) {
            Ok(Self {
                inner: Some(left & right),
            })
        } else {
            Err(MatcherUsed.into())
        }
    }

    #[getter]
    pub fn _used(&self) -> bool {
        self.inner.is_none()
    }
}

/// Low level Python wrapper for Simple matcher and Buffer handler
#[pyclass]
pub struct Streamson {
    collector: Collector,
    handler: Arc<Mutex<handler::Buffer>>,
}

#[pymethods]
impl Streamson {
    /// Create a new instance of Streamson
    ///
    /// # Arguments
    /// * `matches` - a list of valid simple matches (e.g. `{"users"}`, `[]{"name"}`, `[0]{}`)
    #[new]
    pub fn new(matcher: &mut RustMatcher) -> PyResult<Self> {
        let handler = Arc::new(Mutex::new(handler::Buffer::new()));
        let matcher = matcher.inner.take().ok_or(MatcherUsed)?;
        let collector = Collector::new().add_matcher(Box::new(matcher), &[handler.clone()]);
        Ok(Self { collector, handler })
    }

    /// Feeds Streamson processor with data
    ///
    /// # Arguments
    /// * `data` - input data to be processed
    pub fn feed(&mut self, data: &[u8]) -> PyResult<()> {
        if let Err(err) = self.collector.process(data) {
            Err(StreamsonError::from(err).into())
        } else {
            Ok(())
        }
    }

    /// Reads data from Buffer handler
    ///
    /// # Returns
    /// * `None` - if no data present
    /// * `Some(<path>, <bytes>)` if there are some data
    fn pop(&mut self) -> Option<(String, Vec<u8>)> {
        match self.handler.lock().unwrap().pop() {
            Some((path, bytes)) => Some((path, bytes.to_vec())),
            None => None,
        }
    }
}
/// This module is a python module implemented in Rust.
#[pymodule]
fn streamson(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Streamson>()?;
    m.add_class::<RustMatcher>()?;

    Ok(())
}
