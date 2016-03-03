hugin
=====

# Monitor flowcells status

### To deploy hugin:

1. clone repo into your filesystem: `git clone git@github.com:kate-v-stepanova/hugin.git`
2. create a virtual environment: `conda create -n hugin python=2.7`
3. activate virtual environment: `source activate hugin`
4. `cd hugin`
5. install required packages: `python setup.py install`

### Before using hugin
#### `Trello board` must be configured:

1. on <a href="http://trello.com">http://trello.com</a> create a new board `FlowCell tracking` (or any other name)
2. get `api_key` and `api_secret` on <a href="https://trello.com/app-key">https://trello.com/app-key</a>
3. get `api_token` via the following link: <a href="https://trello.com/1/connect?key=api-key&name=flowcell-tracking&response_type=token&scope=read,write"> https://trello.com/1/connect?key=api_key&name=flowcell-tracking&response_type=token&scope=read,write</a>
4. for accessing the trello board, one more value is needed. Open the board, and copy & paste from the address line  `board-ID`: `https://trello.com/b/<board-ID>/flowcell-tracking` 

#### `config file` must be created:

1. default location of the config file is: `~/.hugin/config.yaml`, but it can also be stored anywhere else
2. Config file must contain the following mandatory fields:

```
trello:
      api_key: <api_key>
      token: <token>
      api_secret: <api_secret>
      run_tracking_board: FlowCell tracking
      board_id: <board_id>
data_folders:
    - /path/to/HiSeq_X_data
    - /path/to/hiseq_data
    - /path/to/miseq_data
    - /or/just/path/to/any/data
sample_sheet_path:
    hiseqx: /abs/path/to/samplesheets/HiSeqX
    hiseq: /abs/path/to/samplesheets/hiseq
    miseq: relative/path/to/samplesheets/miseq # relative from the flowcell directory

transfering:
   hiseqx:
      url: <server-url>
      username: <username> # passwordless ssh access must be configured between the preprocessing server and the server where data is transferring
      path: /path/where/the/data/is/being/transferred
   hiseq:
      url: <server-url>
      username: <username>
      path: /path/where/the/data/is/being/transferred
   miseq:
      url: <server-url>
      username: <username>
      path: /path/where/the/data/is/being/transferred
```


### To run hugin:
run a command `hugin --help`

### To test hugin:
`hugin --config-file tests/config.yaml test_flowcells --hiseqx`
(it requires a different config file, which is present in the repo <sub><sup>and contains my passwords - very smart! but otherwise i will forget how to do it</sup></sub>)

