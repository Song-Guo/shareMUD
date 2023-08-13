//SPDX-License-Identifier: UNLICENSED
pragma solidity >= 0.8.18;

contract MUDsharing {

    // Declare state variables of contract
    address public owner;
    struct single_offer{
        uint var_offer_eth;
        uint var_size_data_kb;
        address var_supplier_addr;
    }

    struct single_request{
        bytes32 varUniqueID;
        Description varDescription;
        uint varBudget;
        uint varTimeRequest;
        string varStatus;
        address varConsumerAddr;
    }

    struct Description{
        string var_cpe_h;
        string var_cpe_o;
        string var_mfctr;
        string var_dev;
        string var_mdl;
        string var_fimwr;
    }

    constructor() {
        owner = msg.sender;
    }

    event RequestPublished(address consumer_addr, single_request description);

    uint expire_offer = 10;
    uint expire_select = 20;
    uint expire_submit = 30;
    uint expire_rate = 40;
    mapping(bytes32=>single_request) public RequestMapping;
    mapping(address=>bytes32[]) public addressToID;
    mapping(bytes32=>mapping(address=>single_offer)) public OfferMapping;
    mapping(bytes32=>single_offer[]) public OfferList;
    single_request[] public viewRequests;

    //solidity cannot return a mapping in bulk, 
    //for suppliers to view all avaliable request, need an array of requests
    
    function sendRequest(
        string memory _cpe_h, 
        string memory _cpe_o, 
        string memory _mfctr,
        string memory _dev,
        string memory _mdl,
        string memory _fimwr,
        uint _budget_eth
        ) public {
    //1. input required: manufacturer, device name, model, firmware version, budget (in eth)
        single_request memory CurRequest;
        Description memory _description;
    //2. use input information create struct description
        _description = Description(_cpe_h,_cpe_o,_mfctr,_dev,_mdl,_fimwr);
        uint _time_request = block.timestamp; //current timestamp, since 1970/01/01
        bytes32 _uniqueID = keccak256(abi.encode(msg.sender,_time_request));
    //3.Generate an uniqueID with timestamp and consumer address
        CurRequest = single_request(
            _uniqueID,
            _description,
            _budget_eth,
            _time_request,
            "open",
            msg.sender);
    //4. create struct single_request, then add into a mapping;
    //and push the single_request struct into an array for consumer/supplier to view.
        RequestMapping[_uniqueID] = CurRequest;
        viewRequests.push(CurRequest);
        addressToID[msg.sender].push(_uniqueID);
        emit RequestPublished(msg.sender, CurRequest);
    //5.allow user to lookup uniqueID of their requests (with their address) via another function
    }
    function viewOpenRequests() view public returns(single_request[] memory){
        return viewRequests;
    }
    function viewYourRequests() view public returns(bytes32[] memory){
        return addressToID[msg.sender];
    }
    function offer(bytes32 _uniqueID, uint _offer_eth,uint _size_data_kb) public {
        if(RequestMapping[_uniqueID].varStatus != "open") {
            revert("Request closed!");
        }
        single_request memory CurRequest = RequestMapping[_uniqueID];
        uint _expireTime = CurRequest.varTimeRequest + expire_offer;
        uint _time_offer = block.timestamp;
    //1. supplier can only provide an offer when the request was not closed.
        if(_time_offer > _expireTime) {
            RequestMapping[_uniqueID].varStatus = "expired_offer";
            revert("Request expired! Function offer");
        }
        single_offer memory CurOffer;
    //2. create a struct single_offer, with inputed data
        CurOffer = single_offer(
            _offer_eth,
            _size_data_kb,
            msg.sender
        );
        OfferMapping[_uniqueID][msg.sender] = CurOffer;
        OfferList[_uniqueID].push(CurOffer);
    }

    function viewOfferMapping(bytes32 _uniqueID,address _supplierAddr) view public returns(single_offer memory) {
        return OfferMapping[_uniqueID][_supplierAddr];
    }
    function viewOfferList(bytes32 _uniqueID) view public returns(single_offer[] memory) {
        return OfferList[_uniqueID];
    }
    function select_check(bytes32 _uniqueID, address[] memory _selections) view public returns (address[] memory , uint ) {
    //0. only consumer can call this function; (need modifier or require)
    //1. only when request closed, consumer can make selection (This is not working now)
    //2. validate selection list(input) : all selected address need to be a member of the offer list;
    //2.1 obtain mapping of supplier address to single_offer; address => single_offer;
    //2.2 iterate selection list, if the address consumer provided not in our mapping,
    //raise an error.
        single_request memory _CurRequest = RequestMapping[_uniqueID];
        uint _time_select = _CurRequest.varTimeRequest;
        uint _expire = _CurRequest.varTimeRequest + expire_select;
        if (_time_select > _expire) {
            revert("Request Expired! Function select_check");
        }
        uint _checked_sum_ETH_eth = 0;
        for(uint i=0; i<_selections.length; i++) {
            address _checkAddr = _selections[i];
            single_offer memory _checkOffer = OfferMapping[_uniqueID][_checkAddr];
            _checked_sum_ETH_eth += _checkOffer.var_offer_eth;
            address _check_address = _checkOffer.var_supplier_addr;
            if(_check_address == address(0x0)) {
                revert("Your input contains invalid supplier address!");
            }
        } 
    //3. if selections are valid: return(checked_selections, Sum of ETH in eth)
        return(_selections,_checked_sum_ETH_eth);
    }
    mapping(bytes32=>mapping(address=>bool)) public selectionMapping;

    function select_payment(bytes32 _uniqueID, address[] memory _selection) payable public {
        if(RequestMapping[_uniqueID].varStatus != "open") {
            revert("Request closed!");
        }
        single_request memory _CurRequest = RequestMapping[_uniqueID];
//1. only consumer can make a selection;
        address _caller = msg.sender;
        address _consumerAdd = _CurRequest.varConsumerAddr;
        require(_caller == _consumerAdd,"Only consumer can make selection");
        uint _time_select = block.timestamp;
        uint _expire = _CurRequest.varTimeRequest + expire_select;
        if (_time_select > _expire) {
            RequestMapping[_uniqueID].varStatus = "expired_select";
            revert("Request Expired! Function select_payment");
        }
        uint _sum_ETH_eth = 0 ;
        for(uint i=0; i<_selection.length; i++) {
            address _SelectedSupplierAddr = _selection[i];
            single_offer memory _SelectedOffer = OfferMapping[_uniqueID][_SelectedSupplierAddr];
            uint _CurOffer = _SelectedOffer.var_offer_eth;
            _sum_ETH_eth += _CurOffer;
            selectionMapping[_uniqueID][_SelectedSupplierAddr] = true;
        }
        require(
        msg.value == _sum_ETH_eth * 1 ether,
        "Need to pay enough ETH to publish a request!");

    //2. for each selected supplier(identified by their address), consumer pay ETH to smart contract
    //# need further change: to reduce gas consumption, better calculate the sum of ETH and 
    //send ETH to smart contract in one trasaction 

    }       
    struct supplier_submission{
        address supplier_addr;
        string file_addr;
    }
    mapping(bytes32=>supplier_submission[]) public submissionMapping;
    mapping(bytes32=>mapping(address=>uint)) public submissionStatus;
    //0= not submitted and not rated; 1 = submitted not rated; 2 = submitted and rated; 
    function submit(bytes32 _uniqueID,string memory _IPFSaddr) payable public {
        if(RequestMapping[_uniqueID].varStatus != "open") {
            revert("Request closed!");
        }
    //1. only selected supplier can get paid by delivering MUD to consumer
        address _supplierAddr = msg.sender;
        if(selectionMapping[_uniqueID][_supplierAddr] != true) {
            revert("You are not selected!");
        }
        //Expire: if failed to submit, the Ether is reverted to consumer; 
        //or the consumer can request to revert the money
        //Note avoid double payment 
        single_request memory CurRequest = RequestMapping[_uniqueID];
        uint _expireTime = CurRequest.varTimeRequest + expire_submit;
        uint _time_offer = block.timestamp;
    //1. supplier can only provide an offer when the request was not closed.
        if(_time_offer > _expireTime) {
            address payable _CurConsumer = payable(RequestMapping[_uniqueID].varConsumerAddr);
            uint _CurOffer =  OfferMapping[_uniqueID][_supplierAddr].var_offer_eth;
            _CurConsumer.transfer(10**18**_CurOffer);
            selectionMapping[_uniqueID][_supplierAddr] = false;
            RequestMapping[_uniqueID].varStatus = "expired_submit";
            revert("Request expired! Function Submit");
            //if supplier failed to submit before expiry:
            //1. return ETH to consumer
            //2. make supplier unselected (avoid double payment)
            //3. revert the function call
        }
    //2. need to get the price of offer
        uint _price_in_eth;
        _price_in_eth = OfferMapping[_uniqueID][_supplierAddr].var_offer_eth;
    //3. submit MUD address to mapping submissionMapping;
        supplier_submission memory curSubmission;
        curSubmission = supplier_submission(msg.sender,_IPFSaddr);
        submissionMapping[_uniqueID].push(curSubmission);
    //4. supplier get paid by smart contract.
        address payable _provider_addr = payable(_supplierAddr);
        _provider_addr.transfer(10**18*_price_in_eth);
        selectionMapping[_uniqueID][_supplierAddr] = false;
    //5. Remove selection to avoid double payment;
        submissionStatus[_uniqueID][_supplier_addr] = true;
    }
    function view_submission(bytes32 _uniqueID) view public returns(supplier_submission[] memory) {
        return(submissionMapping[_uniqueID]);
    }
    struct single_rate{
        uint varRate;
        bytes32 varUniqueID;
    }
    function refund(bytes32 _uniqueID, address _supplier) payable public{
        single_request memory _CurRequest = RequestMapping[_uniqueID];
        uint _time_select = _CurRequest.varTimeRequest;
        uint _expire = _CurRequest.varTimeRequest + expire_submit;
        if (_time_select > _expire) {
            revert("Request Expired! Function select_check");
        }
        address _Consumer = CurRequest.varConsumerAddr;
        require(msg.sender == _Consumer,"Only Consumer can call refund!")
        if(selectionMapping[_uniqueID][_supplier] != true) {
            revert("supplier not selected!");
        }
        if(submissionStatus[_uniqueID][_supplier] = true) {
            revert("Supplier already submitted!");
        }
        selectionMapping[_uniqueID][_supplier] = false;
        uint _price_in_eth;
        _price_in_eth = OfferMapping[_uniqueID][_supplier].var_offer_eth;
        address payable _Consumer = payable(_Consumer);
        _Consumer.transfer(10**18**_price_in_eth);
    }
    function check_submission(bytes32 _uniqueID) payable public {
        //function: let consumer remove all ETH from those suppliers failed to submit before due time
        //May able to implement with DApp
        }
        
    mapping(address=>single_rate[]) rateMapping;

    function rate_supplier(bytes32 _uniqueID, address _supplierAddr, uint _rate) public {
        //function: 
        address _RequestOwner = RequestMapping[_uniqueID].varConsumerAddr;
        require(msg.sender == _RequestOwner, "You are not eligible to rate this transaction");
        //check eligibility: only consumer of certain transaction can rate other suppliers
        //check eligibility: supplier must be a selected supplier of that specific request
        require(submissionStatus[_uniqueID][_supplierAddr] = true, "Only submitted supplier of this transaction can be rated!");
        _CurRate = single_rate(_rate,_uniqueID);
        rateMapping[supplier_addr].push(_CurRate);
        submissionStatus[_uniqueID][supplier_addr] = false;
    }
    function rate_check(bytes32 _uniqueID) public {
        //Function: all expired rate should be automatically set to full mark 
    }


}



//next steps:
//1. use modifier to check eligibility (e.g. only consumer can make a selection and pay ETH to supplier;
// only selected supplier can submit a MUD file address and get ETH, etc.).
//2. Expire check: this function is not operational now.
//3. Interactive: The current procedure requires consumer and suppliers mannually check every step, and 
//these functions cannot interact with user. -- Event and emit


