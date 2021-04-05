use super::BaseHandler;
use crate::StreamsonError;
use pyo3::prelude::*;
use std::{
    fs, io,
    str::FromStr,
    sync::{Arc, Mutex},
};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct FileHandler {
    pub file_inner: Arc<Mutex<handler::Output<fs::File>>>,
}

#[pymethods]
impl FileHandler {
    /// Create instance of Indenter handler
    #[new]
    #[args(write_path = "false")]
    pub fn new(path: String, write_path: bool) -> Result<(Self, BaseHandler), PyErr> {
        let file_inner = Arc::new(Mutex::new(
            handler::Output::<fs::File>::from_str(&path)
                .map_err(|e| StreamsonError::new_err(e.to_string()))?
                .set_write_path(write_path),
        ));
        Ok((
            Self {
                file_inner: file_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(file_inner))),
            },
        ))
    }
}

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct StdoutHandler {
    pub stdout_inner: Arc<Mutex<handler::Output<io::Stdout>>>,
}

#[pymethods]
impl StdoutHandler {
    /// Create instance of Indenter handler
    #[new]
    #[args(write_path = "false")]
    pub fn new(write_path: bool) -> (Self, BaseHandler) {
        let stdout_inner = Arc::new(Mutex::new(
            handler::Output::<io::Stdout>::new(io::stdout()).set_write_path(write_path),
        ));
        (
            Self {
                stdout_inner: stdout_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(stdout_inner))),
            },
        )
    }
}
