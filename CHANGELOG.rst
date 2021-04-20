4.0.0 (2021-04-20)
------------------

* upgraded streamson-lib to 7.0.1
* handlers redone (streamson-lib uses streaming handlers)
* added can use handlers from streamson-lib
* added all strategy
* API updated to be compatible with newer version of streamson-lib
* running test on macos and windows
* use Faker to generate nicer input for test data

3.1.0 (2020-11-24)
------------------

* upgraded streamson-lib to 6.2
* added streamson binary - passes tests of stremson-bin
* tox integration
* refactor to use strategies similar to streamson-lib
* python 3.9 compatibility

3.0.0 (2020-09-03)
------------------

* overall api changes
* new async extractor (`extract_async`)
* new file extractor (`extractd_fd`)
* new benchmark options
* added options to suppress path extraction (speeds up the extraction)
* fixing benchmarks
* various speed improvements
* ability to extract raw data (only bytes not json)

2.0.0 (2020-07-13)
------------------

* update to a newer version of streamson
* is about 24% faster, but doesn't check whether the input is valid utf8 string

1.0.0 (2020-07-03)
------------------

* refactor so it is possible to use different matchers

0.1.0 (2020-06-08)
------------------

* extract_iter function implemented
* initial version
