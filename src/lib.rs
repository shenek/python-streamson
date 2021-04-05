pub mod handler;
pub mod strategy;

pub use handler::{
    AnalyserHandler, BaseHandler, BufferHandler, FileHandler, IndenterHandler, IndexerHandler,
    PythonHandler, PythonToken, RegexHandler, ReplaceHandler, ShortenHandler, StdoutHandler,
    UnstringifyHandler,
};
pub use strategy::{Convert, Extract, Filter, PythonStrategy, Trigger};

use pyo3::{
    class::{basic::CompareOp, PyNumberProtocol, PyObjectProtocol},
    create_exception, exceptions,
    prelude::*,
};
use std::{convert::TryFrom, str::FromStr};
use streamson_lib::{matcher, strategy::Output, Path};

create_exception!(streamson, StreamsonError, exceptions::PyValueError);

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
                matcher::Simple::from_str(&path)
                    .map_err(|e| StreamsonError::new_err(e.to_string()))?,
            ),
        })
    }

    /// Create a new instance of depth matcher
    ///
    /// # Arguments
    /// * `depth_str` - string which can be parsed to depth matcher
    #[staticmethod]
    pub fn depth(depth_str: String) -> PyResult<Self> {
        Ok(Self {
            inner: matcher::Combinator::new(
                matcher::Depth::from_str(&depth_str)
                    .map_err(|e| StreamsonError::new_err(e.to_string()))?,
            ),
        })
    }

    /// Create a matcher which will match by regex
    #[staticmethod]
    pub fn regex(regex: String) -> PyResult<Self> {
        Ok(Self {
            inner: matcher::Combinator::new(
                matcher::Regex::from_str(&regex)
                    .map_err(|e| StreamsonError::new_err(e.to_string()))?,
            ),
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

/// Python class which represents the output data
#[pyclass]
#[derive(Debug, Clone)]
pub struct PythonOutput {
    #[pyo3(get)]
    kind: String,
    #[pyo3(get)]
    path: Option<String>,
    #[pyo3(get)]
    data: Option<Vec<u8>>,
}

impl From<Output> for PythonOutput {
    fn from(output: Output) -> Self {
        match output {
            Output::Start(path_opt) => Self {
                kind: "Start".into(),
                path: path_opt.map(|e| e.to_string()),
                data: None,
            },
            Output::Data(data) => Self {
                kind: "Data".into(),
                path: None,
                data: Some(data),
            },
            Output::End => Self {
                kind: "End".into(),
                path: None,
                data: None,
            },
        }
    }
}

#[pymethods]
impl PythonOutput {
    /// Create instance of PythonOutput handler
    #[staticmethod]
    pub fn make_start(path: Option<String>) -> Result<Self, PyErr> {
        if let Some(path_str) = path {
            let strref: &str = &path_str;
            Ok(Output::Start(Some(
                Path::try_from(strref).map_err(|e| StreamsonError::new_err(e.to_string()))?,
            ))
            .into())
        } else {
            Ok(Output::Start(None).into())
        }
    }

    #[staticmethod]
    pub fn make_data(data: Vec<u8>) -> Self {
        Output::Data(data).into()
    }

    #[staticmethod]
    pub fn make_end() -> Self {
        Output::End.into()
    }
}

#[pyproto]
impl PyObjectProtocol for PythonOutput {
    fn __richcmp__(&self, other: Self, op: CompareOp) -> PyResult<bool> {
        match op {
            CompareOp::Eq => {
                Ok(other.data == self.data && other.kind == self.kind && other.path == self.path)
            }
            _ => unimplemented!(),
        }
    }
}
/// This module is a python module implemented in Rust.
#[pymodule]
fn streamson(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Convert>()?;
    m.add_class::<Extract>()?;
    m.add_class::<Filter>()?;
    m.add_class::<RustMatcher>()?;
    m.add_class::<Trigger>()?;
    m.add_class::<AnalyserHandler>()?;
    m.add_class::<FileHandler>()?;
    m.add_class::<BaseHandler>()?;
    m.add_class::<BufferHandler>()?;
    m.add_class::<BufferHandler>()?;
    m.add_class::<IndexerHandler>()?;
    m.add_class::<IndenterHandler>()?;
    m.add_class::<PythonHandler>()?;
    m.add_class::<RegexHandler>()?;
    m.add_class::<ReplaceHandler>()?;
    m.add_class::<StdoutHandler>()?;
    m.add_class::<ShortenHandler>()?;
    m.add_class::<UnstringifyHandler>()?;
    m.add_class::<PythonToken>()?;
    m.add_class::<PythonOutput>()?;

    Ok(())
}
