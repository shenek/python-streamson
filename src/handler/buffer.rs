use super::BaseHandler;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(extends=BaseHandler)]
#[derive(Clone)]
pub struct BufferHandler {
    pub buffer_inner: Arc<Mutex<handler::Buffer>>,
}

#[pymethods]
impl BufferHandler {
    /// Create instance of Buffer handler
    #[new]
    #[args(use_path = "true", max_size = "None")]
    pub fn new(use_path: bool, max_size: Option<usize>) -> (Self, BaseHandler) {
        let buffer_inner = Arc::new(Mutex::new(
            handler::Buffer::new()
                .set_use_path(use_path)
                .set_max_buffer_size(max_size),
        ));
        (
            Self {
                buffer_inner: buffer_inner.clone(),
            },
            BaseHandler {
                inner: Arc::new(Mutex::new(handler::Group::new().add_handler(buffer_inner))),
            },
        )
    }

    /// Remove first element from the buffer
    pub fn pop_front(&mut self) -> Option<(Option<String>, Vec<u8>)> {
        self.buffer_inner.lock().unwrap().pop()
    }
}
