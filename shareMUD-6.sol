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
    struct single_submission{
        bytes32 var_UID;
        string var_fileAddr;
        address var_supplierAddr;
    }
    struct single_rate{
        bytes32 varUID;
        uint varRate;
        address varSupplierAddr;
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
    mapping(bytes32=>mapping(address=>bool)) public selectionBool;
    mapping(bytes32=>mapping(address=>bool)) public submissionBool;
    mapping(bytes32=>mapping(address=>bool)) public refundBool;
    mapping(bytes32=>mapping(address=>bool)) public rateBool;
    mapping(bytes32=>single_submission[]) public submissionList;
    mapping(bytes32=>mapping(address=>single_rate[])) public rateList;
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
            msg.sender);
    //4. create struct single_request, then add into a mapping;
    //and push the single_request struct into an array for consumer/supplier to view.
        RequestMapping[_uniqueID] = CurRequest;
        viewRequests.push(CurRequest);
        addressToID[msg.sender].push(_uniqueID);
        emit RequestPublished(msg.sender, CurRequest);
    //5.allow user to lookup uniqueID of their requests (with their address) via another function
    }
    function offer(bytes32 _uniqueID, uint _offer_eth,uint _size_data_kb) public {
        single_request memory CurRequest = RequestMapping[_uniqueID];
        uint _expireTime = CurRequest.varTimeRequest + expire_offer;
        uint _time_offer = block.timestamp;
    //1. supplier can only provide an offer when the request was not closed.
        if(_time_offer > _expireTime) {
            revert("Expired_Offer");
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
    function select_payment(bytes32 _uniqueID, address[] memory _selectionList) payable public {
        single_request memory _CurRequest = RequestMapping[_uniqueID];
        address _consumerAdd = _CurRequest.varConsumerAddr;
        require(_consumerAdd == msg.sender,"Only consumer can make a selection");
        uint _time_select = block.timestamp;
        uint _expire = _CurRequest.varTimeRequest + expire_select;
        if(_time_select > _expire) {
            revert("Request Expired by select_payment");
        }
        uint _sum_ETH_eth = 0 ;
        for(uint i=0; i<_selectionList.length; i++) {
            address _SelectedSupplierAddr = _selectionList[i];
//            single_offer memory _checkOffer = OfferMapping[_uniqueID][_SelectedSupplierAddr];
//            address _check_address = _checkOffer.var_supplier_addr;
//            if(_check_address == address(0x0)) {
//                revert("InvalidAddr");
//            }
            single_offer memory _SelectedOffer = OfferMapping[_uniqueID][_SelectedSupplierAddr];
            uint _CurOffer = _SelectedOffer.var_offer_eth;
            _sum_ETH_eth += _CurOffer;
            selectionBool[_uniqueID][_SelectedSupplierAddr] = true;
            submissionBool[_uniqueID][_SelectedSupplierAddr] = false;
            refundBool[_uniqueID][_SelectedSupplierAddr] = false;
            rateBool[_uniqueID][_SelectedSupplierAddr] = false;
        }
        require(
        msg.value == _sum_ETH_eth * 1 ether,
        "NoEnoughEth");
    }
    function submit(bytes32 _uniqueID,string memory _MUDaddr) payable public {
        single_request memory _CurRequest = RequestMapping[_uniqueID];
        require(selectionBool[_uniqueID][msg.sender] == true, "NotSelected");
        require(submissionBool[_uniqueID][msg.sender] == false, "NoDoublePayment");
        uint _time_submit = block.timestamp;
        uint _expire = _CurRequest.varTimeRequest + expire_submit;
        address _supplierAddr = msg.sender;
        if(_time_submit > _expire) {
            address payable _PayConsumer = payable(_CurRequest.varConsumerAddr);
            uint _CurOffer =  OfferMapping[_uniqueID][_supplierAddr].var_offer_eth;
            _PayConsumer.transfer(10**18**_CurOffer);
            submissionBool[_uniqueID][msg.sender] = true;
            revert("Request Expired, submit overdue");
        }
        uint _price_in_eth = OfferMapping[_uniqueID][_supplierAddr].var_offer_eth;
        single_submission memory CurSub = single_submission(_uniqueID,_MUDaddr,_supplierAddr);
        submissionList[_uniqueID].push(CurSub);
        address payable _PaySupplier = payable(_supplierAddr);
        _PaySupplier.transfer(10**18**_price_in_eth);
        submissionBool[_uniqueID][msg.sender] = true;
    }
    function refund(bytes32 _uniqueID, address _supplierAddr) payable public {
        single_request memory _CurRequest = RequestMapping[_uniqueID];
        require(RequestMapping[_uniqueID].varConsumerAddr == msg.sender, "NotConsumer");
        require(selectionBool[_uniqueID][msg.sender] == true, "NotSelected");
        uint _time_submit = block.timestamp;
        uint _expire = _CurRequest.varTimeRequest + expire_submit;
        if(_time_submit < _expire) {
            revert("Request when overdue");
        }
        require(submissionBool[_uniqueID][msg.sender] == false, "NoDoublePayment");
        address payable _PayConsumer = payable(RequestMapping[_uniqueID].varConsumerAddr);
        uint _CurOffer =  OfferMapping[_uniqueID][_supplierAddr].var_offer_eth;
        _PayConsumer.transfer(10**18**_CurOffer);
        submissionBool[_uniqueID][msg.sender] = true;
        refundBool[_uniqueID][msg.sender] = true;
    }

    function rate(bytes32 _uniqueID, address _supplierAddr, uint _rate) public {
        single_request memory _CurRequest = RequestMapping[_uniqueID];
        address _consumer = _CurRequest.varConsumerAddr;
        require(msg.sender == _consumer, "Only consumer can rate a supplier");
        require(rateBool[_uniqueID][_supplierAddr] == false, "RateExist");
        require(selectionBool[_uniqueID][_supplierAddr] == true,"NotSelected");
        require(submissionBool[_uniqueID][_supplierAddr] == true,"NotSubmitted");
        require(refundBool[_uniqueID][_supplierAddr] == false, "Refunded");
        uint _time_submit = block.timestamp;
        uint _expire = _CurRequest.varTimeRequest + expire_rate;
        require(_rate>0,"Rate>0");
        require(_rate<=50,"Rate<=50");
        if(_time_submit > _expire) {
            single_rate memory _CurRate = single_rate(_uniqueID,50,_supplierAddr);
            rateList[_uniqueID][_supplierAddr].push(_CurRate);
            rateBool[_uniqueID][_supplierAddr] = true;
            revert("Expired_Rate");
        }
        single_rate memory _CurRate = single_rate(_uniqueID,_rate,_supplierAddr);
        rateList[_uniqueID][_supplierAddr].push(_CurRate);
        rateBool[_uniqueID][_supplierAddr] = true;
    }

    function forgot_rate(bytes32 _uniqueID) public {
        single_request memory _CurRequest = RequestMapping[_uniqueID];
        address _supplierAddr = msg.sender;
        require(rateBool[_uniqueID][_supplierAddr] == false, "RateExist");
        require(selectionBool[_uniqueID][_supplierAddr] == true,"NotSelected");
        require(submissionBool[_uniqueID][_supplierAddr] == true,"NotSubmitted");
        require(refundBool[_uniqueID][_supplierAddr] == false, "Refunded");
        uint _time_submit = block.timestamp;
        uint _expire = _CurRequest.varTimeRequest + expire_rate;
        if(_time_submit > _expire) {
            single_rate memory _CurRate = single_rate(_uniqueID,50,_supplierAddr);
            rateList[_uniqueID][_supplierAddr].push(_CurRate);
            rateBool[_uniqueID][_supplierAddr] = true;
            revert("Expired_Rate");
        }
    }

}