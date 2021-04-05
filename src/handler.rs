pub mod analyser;
pub mod base;
pub mod buffer;
pub mod indenter;
pub mod indexer;
pub mod output;
pub mod python;
pub mod regex;
pub mod replace;
pub mod shorten;
pub mod unstringify;

pub use analyser::AnalyserHandler;
pub use base::BaseHandler;
pub use buffer::BufferHandler;
pub use indenter::IndenterHandler;
pub use indexer::IndexerHandler;
pub use output::{FileHandler, StdoutHandler};
pub use python::PythonHandler;
pub use regex::RegexHandler;
pub use replace::ReplaceHandler;
pub use shorten::ShortenHandler;
pub use unstringify::UnstringifyHandler;

use pyo3::prelude::*;
use streamson_lib::streamer;

#[pyclass]
pub struct PythonParsedKind {
    pub kind: String,
}

impl From<streamer::ParsedKind> for PythonParsedKind {
    fn from(kind: streamer::ParsedKind) -> Self {
        match kind {
            streamer::ParsedKind::Obj => Self { kind: "Obj".into() },
            streamer::ParsedKind::Arr => Self { kind: "Arr".into() },
            streamer::ParsedKind::Str => Self { kind: "Str".into() },
            streamer::ParsedKind::Num => Self { kind: "Num".into() },
            streamer::ParsedKind::Null => Self {
                kind: "Null".into(),
            },
            streamer::ParsedKind::Bool => Self {
                kind: "Bool".into(),
            },
        }
    }
}

#[pyclass]
pub struct PythonToken {
    pub token: String,
    pub idx: Option<usize>,
    pub kind: Option<PythonParsedKind>,
}

impl From<streamer::Token> for PythonToken {
    fn from(token: streamer::Token) -> Self {
        match token {
            streamer::Token::Start(idx, kind) => Self {
                token: "Start".into(),
                idx: Some(idx),
                kind: Some(kind.into()),
            },
            streamer::Token::End(idx, kind) => Self {
                token: "End".into(),
                idx: Some(idx),
                kind: Some(kind.into()),
            },
            streamer::Token::Separator(idx) => Self {
                token: "Separator".into(),
                idx: Some(idx),
                kind: None,
            },
            streamer::Token::Pending => Self {
                token: "Pending".into(),
                idx: None,
                kind: None,
            },
        }
    }
}
