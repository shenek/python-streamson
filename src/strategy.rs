pub mod all;
pub mod convert;
pub mod extract;
pub mod filter;
pub mod trigger;

pub use all::All;
pub use convert::Convert;
pub use extract::Extract;
pub use filter::Filter;
pub use trigger::Trigger;

use super::{PythonOutput, StreamsonError};
use pyo3::prelude::*;
use streamson_lib::strategy;

pub trait PythonStrategy<S>
where
    S: strategy::Strategy,
{
    /// Get the strategy
    fn get_strategy(&mut self) -> &mut S;

    /// Processes input data
    fn _process(&mut self, input_data: &[u8]) -> PyResult<Vec<PythonOutput>> {
        match self.get_strategy().process(input_data) {
            Err(err) => Err(StreamsonError::new_err(err.to_string())),
            Ok(output) => Ok(output.into_iter().map(|e| e.into()).collect()),
        }
    }

    /// Functions which is triggered when the input has stopped
    fn _terminate(&mut self) -> PyResult<Vec<PythonOutput>> {
        match self.get_strategy().terminate() {
            Err(err) => Err(StreamsonError::new_err(err.to_string())),
            Ok(output) => Ok(output.into_iter().map(|e| e.into()).collect()),
        }
    }
}
