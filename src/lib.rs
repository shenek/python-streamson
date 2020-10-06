pub mod extract;
pub mod trigger;

pub use extract::Extract;
pub use trigger::{PythonHandler, Trigger};

use pyo3::{class::PyNumberProtocol, create_exception, exceptions, prelude::*};

use streamson_lib::{error, matcher};

create_exception!(streamson, StreamsonError, exceptions::ValueError);
create_exception!(streamson, MatcherUsed, exceptions::RuntimeError);

impl From<error::General> for StreamsonError {
    fn from(_gerror: error::General) -> Self {
        Self
    }
}

impl From<error::Matcher> for StreamsonError {
    fn from(_gerror: error::Matcher) -> Self {
        Self
    }
}

/// Python wrapper around matchers
#[pyclass]
#[derive(Debug)]
pub struct RustMatcher {
    inner: matcher::Combinator,
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
            inner: matcher::Combinator::new(
                matcher::Simple::new(&path).map_err(StreamsonError::from)?,
            ),
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
            inner: matcher::Combinator::new(matcher::Depth::new(min_depth, max_depth)),
        })
    }
}

#[pyproto]
impl PyNumberProtocol for RustMatcher {
    /// Inverts the matcher
    fn __invert__(&self) -> Self {
        Self {
            inner: !self.inner.clone(),
        }
    }

    /// One of the matcher should match
    fn __or__(lhs: PyRef<'p, Self>, rhs: PyRef<'p, Self>) -> Self {
        Self {
            inner: lhs.inner.clone() | rhs.inner.clone(),
        }
    }

    /// All matchers should match
    fn __and__(lhs: PyRef<'p, Self>, rhs: PyRef<'p, Self>) -> Self {
        Self {
            inner: lhs.inner.clone() & rhs.inner.clone(),
        }
    }
}

/// This module is a python module implemented in Rust.
#[pymodule]
fn streamson(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Extract>()?;
    m.add_class::<RustMatcher>()?;
    m.add_class::<Trigger>()?;
    m.add_class::<PythonHandler>()?;

    Ok(())
}
