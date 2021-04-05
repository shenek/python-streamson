use pyo3::{class::PyNumberProtocol, prelude::*};
use std::sync::{Arc, Mutex};
use streamson_lib::handler;

#[pyclass(subclass)]
#[derive(Clone)]
pub struct BaseHandler {
    pub inner: Arc<Mutex<handler::Group>>,
}

#[pymethods]
impl BaseHandler {
    /// Create instance of CombinatorHandler
    #[new]
    pub fn new() -> Self {
        Self {
            inner: Arc::new(Mutex::new(handler::Group::new())),
        }
    }

    pub fn merge(&self, other: &Self) -> Self {
        let mut joined = handler::Group::new();
        self.inner
            .lock()
            .unwrap()
            .subhandlers()
            .iter()
            .for_each(|h| joined.add_handler_mut(h.clone()));
        other
            .inner
            .lock()
            .unwrap()
            .subhandlers()
            .iter()
            .for_each(|h| joined.add_handler_mut(h.clone()));
        return Self {
            inner: Arc::new(Mutex::new(joined)),
        };
    }
}

#[pyproto]
impl PyNumberProtocol for BaseHandler {
    /// Joins handlers together
    fn __add__(lhs: PyRef<'p, Self>, rhs: PyRef<'p, Self>) -> Self {
        lhs.merge(&rhs)
    }
}
