use pyo3::{class::PyNumberProtocol, create_exception, exceptions, prelude::*};

use streamson_lib::{error, matcher, strategy};

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

/// Low level Python wrapper for Simple matcher and Buffer handler
#[pyclass]
pub struct Streamson {
    extract: strategy::Extract,
}

#[pymethods]
impl Streamson {
    /// Create a new instance of Streamson
    ///
    /// # Arguments
    /// * `matches` - a list of valid simple matches (e.g. `{"users"}`, `[]{"name"}`, `[0]{}`)
    /// * `export_path` - indicator whether path is required in further processing
    #[new]
    pub fn new(matcher: &RustMatcher, export_path: Option<bool>) -> PyResult<Self> {
        let export_path = export_path.unwrap_or(true);
        let mut extract = strategy::Extract::new().set_export_path(export_path);
        extract.add_matcher(Box::new(matcher.inner.clone()));
        Ok(Self { extract })
    }

    /// Feeds Streamson processor with data
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

/// This module is a python module implemented in Rust.
#[pymodule]
fn streamson(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Streamson>()?;
    m.add_class::<RustMatcher>()?;

    Ok(())
}
