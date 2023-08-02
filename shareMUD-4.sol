pragma solidity >= 0.8.18;

contract MUDsharing {

    // Declare state variables of contract
    address public owner;
    struct single_offer{
        bytes32 var_UniqueID;
        uint var_offer_eth;
        uint var_size_data_kb;
        address var_supplier_addr;
    }

    struct single_request{
        bytes32 varUniqueID;
        uint varTimeRequest;
        address varConsumerAddr;
        Description varDescription;
        uint varBudget;
        string varStatus;
        uint varExpire;
    }

    struct Description{
        string mfctr;
        string dev;
        string mdl;
        string fimwr;
    }

    constructor() {
        owner = msg.sender;
    }

    event RequestPublished(address consumer_addr, single_request description);

    mapping(bytes32=>single_request) public RequestMapping;
    //mapping, key = uniqueID, store struct single_request(one request, multiple offers)
    mapping(address=>bytes32[]) public addressToID;
    mapping(bytes32=>mapping(address=>single_offer)) public OfferMapping;
    mapping(bytes32=>single_offer[]) public OfferList;
    //mapping, key = uniqueID, store a list of struct single_offer(one request, multiple offers)
    //mapping(address=>uint) public rate;
    single_request[] public viewRequests;
    //solidity cannot return a mapping in bulk, 
    //for suppliers to view all avaliable request, need an array of requests
    function sendRequest(
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
        _description = Description(_mfctr,_dev,_mdl,_fimwr);
        uint _time_request = block.timestamp; //current timestamp, since 1970/01/01
        bytes32 _uniqueID = keccak256(abi.encode(msg.sender,_time_request));
    //3.Generate an uniqueID with timestamp and consumer address
        CurRequest = single_request(
            _uniqueID,
            _time_request,
            msg.sender,
            _description,
            _budget_eth,
            "open",
            120);
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
        single_request memory CurRequest = RequestMapping[_uniqueID];
        uint _expireTime = CurRequest.varTimeRequest + CurRequest.varExpire;
        uint _time_offer = block.timestamp;
    //1. supplier can only provide an offer when the request was not closed.
        require(_time_offer < _expireTime, "Request closed!");
        if(_time_offer< _expireTime) {
            RequestMapping[_uniqueID].varStatus = "closed";
        }
        single_offer memory CurOffer;
    //2. create a struct single_offer, with inputed data
        CurOffer = single_offer(
            _uniqueID,
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
        //single_request memory _CurRequest = RequestMapping[_uniqueID];
        //uint _expireTime = _CurRequest.varTimeRequest + _CurRequest.varExpire;
        //uint _time_selection = block.timestamp;
        //require(_time_selection > _expireTime, "only when request was closed consumer can make selection");
        //if(_time_selection > _expireTime) {
        //    RequestMapping[_uniqueID].varStatus = "closed";
        //}
    //2. validate selection list(input) : all selected address need to be a member of the offer list;
    //2.1 obtain mapping of supplier address to single_offer; address => single_offer;
    //2.2 iterate selection list, if the address consumer provided not in our mapping,
    //raise an error.
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
        //single_request memory _CurRequest = RequestMapping[_uniqueID];
        //require(msg.sender = _CurRequest.varConsumerAddr, "only consumer can make selection");
//1. only consumer can make a selection;
        uint _sum_ETH_eth = 0 ;
        for(uint i=0; i<_selection.length; i++) {
            address _SelectedSupplierAddr = _selection[i];
            single_offer memory _SelectedOffer = OfferMapping[_uniqueID][_SelectedSupplierAddr];
            uint _CurOffer = _SelectedOffer.var_offer_eth;
            _sum_ETH_eth += _CurOffer;
            selectionMapping[_uniqueID][_SelectedSupplierAddr] = true;
        }
        //payable(msg.sender).transfer(_sum_ETH_eth);
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
        single_request currentRequest;
    }
    mapping(bytes32=>supplier_submission[]) public submissionMapping;
    function submit(bytes32 _uniqueID,string memory _IPFSaddr) payable public {
    //1. only selected supplier can get paid by delivering MUD to consumer
        address _supplierAddr = msg.sender;
        if(selectionMapping[_uniqueID][_supplierAddr] != true) {
            revert("You are not selected!");
        }
    //2. need to get the price of offer
        uint _price_in_eth;
        _price_in_eth = OfferMapping[_uniqueID][_supplierAddr].var_offer_eth;
    //3. submit MUD address to mapping submissionMapping;
        supplier_submission memory curSubmission;
        curSubmission = supplier_submission(msg.sender,_IPFSaddr,RequestMapping[_uniqueID]);
        submissionMapping[_uniqueID].push(curSubmission);
    //4. supplier get paid by smart contract.
        address payable _provider_addr = payable(_supplierAddr);
        _provider_addr.transfer(10**18*_price_in_eth);
    }
    function view_submission(bytes32 _uniqueID) view public returns(supplier_submission[] memory) {
        return(submissionMapping[_uniqueID]);
    }
    //mapping(address=>uint) rateMapping;
    //mapping(address=>uint) rateCounter;
    //funcion rate(uint _rate, address _supplierAddr, bytes32 _uniqueID) public {
    //    address _RequestOwner = RequestMapping[_uniqueID].varConsumerAddr;
    //    require(msg.sender == _RequestOwner, "You are not eligible to rate this transaction")
    //    //Need to check eligibility: supplier must be a member of that specific request, and need to be selected
    //    uint ExistingRate = rateMapping[_supplierAddr];
    //    uint ExistingRateCount = rateCounter[_supplierAddr];
    //    uint CurRating = (ExistingRate * ExistingRateCount + _rate) / (ExistingRateCount + 1);
    //   rateCounter[_supplierAddr] +=1;
    //    rateMapping[_supplierAddr] = CurRating;
    //}
    //function ViewRate(address _supplierAddr) public returns(uint) {
    //    return(rateMapping[_supplierAddr],rateCounter[_supplierAddr]);
    //}
}



//next steps:
//1. use modifier to check eligibility (e.g. only consumer can make a selection and pay ETH to supplier;
// only selected supplier can submit a MUD file address and get ETH, etc.).
//2. Expire check: this function is not operational now.
//3. Interactive: The current procedure requires consumer and suppliers mannually check every step, and 
//these functions cannot interact with user. -- Event and emit