// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract VoteStorage {
    struct Vote {
        bytes signature;
        bytes randomNumber;
    }

    Vote[] private votes;

    /// @dev 存储选票
    function storeVote(bytes memory _signature, bytes memory _randomNumber) public {
        votes.push(Vote(_signature, _randomNumber));
    }

    /// @dev 获取选票总数
    function getVotesCount() public view returns (uint256) {
        return votes.length;
    }

    /// @dev 根据索引获取选票信息
    function getVote(uint256 index) public view returns (bytes memory, bytes memory) {
        require(index < votes.length, "Index out of range");
        Vote memory vote = votes[index];
        return (vote.signature, vote.randomNumber);
    }
}