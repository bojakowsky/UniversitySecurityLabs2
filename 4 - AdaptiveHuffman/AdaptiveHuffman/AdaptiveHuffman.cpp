// AdaptiveHuffman.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <iostream>
#include <fstream>
#include <string>
#include <bitset>
#include <queue>
#include <vector>
#include <sstream>
using namespace std;

// Global variable for presentation purposes
string buffer = "";

class Node {
public:
	string ch = "";
	int quantity = 0;
	Node *left = nullptr;
	Node *right = nullptr;
	Node *parent = nullptr;

	Node() {
		quantity = 1; // ESC Null node
		ch = "ESC";
	}

	Node(int quantity, string ch, Node* parent) {
		this->ch = ch;
		this->quantity = quantity;
		this->parent = parent;
	}

	Node(int quantity)
	{
		this->quantity = quantity;
	}
};



class HuffmanTree {
public:
	struct res {
		int i;
		bool ESC = true;

		res(int i) {
			this->i = i;
		}
	};

	Node *root = nullptr;
	string encoded = "";
	HuffmanTree() {
		root = new Node();
	}

	void decodeBin(string bin) {
		int i = stoi(bin, nullptr, 2);
		string decoded = string(1, (char)i);
		std::cout << decoded;

		//add to tree
		encode(decoded);
	}

	void decodeFile(string bin) {
		decode(bin.substr(0, 7));
		bin = bin.substr(7, bin.length() - 7);
		res r(0);
		while (bin.length()) {
			r = decode(bin);
				bin = bin.substr(r.i, bin.length() - r.i);
		}
	}

	res decode(string bin) {
		if (root->ch == "ESC") {
			decodeBin(bin);
		}

		else {
			Node *runner = root;
			for (int i = 0; i < bin.length(); ++i) {
				if (string(1, bin[i]) == "0") {
					if (runner->left != nullptr)
						runner = runner->left;
				}
				else {
					if (runner->right != nullptr)
						runner = runner->right;
				}
				
				if (runner->right == nullptr && runner->left == nullptr && runner != nullptr) {
					if (runner->ch == "ESC") {
						decodeBin(bin.substr(i + 1, 7));	
						res r(i + 8);
						return r;
					}
					else if (runner->ch != "") {
						encode(runner->ch);
						std::cout << runner->ch;
						res r(i + 1);
						r.ESC = false;
						return r;
					}

				}
			}

		}
	}

	void encode(string val) {
		Node *node = root;
		if (node == nullptr) return;

		std::queue<Node*> huff_queue;
		huff_queue.push(node);

		std::queue<Node*> bfs;
		bfs.push(node);
		bool added = false;
		while (!bfs.empty())
		{
			Node *current = bfs.front();
			
			if (current->ch == val)
			{
				current->quantity += 1;
				//incQuantities(current);
				added = true;
				buffer = getEncodedSymbol(val, current, false);
			}

			else if (current->ch == "ESC" && added == false)
			{
				buffer = getEncodedSymbol(val, current);
				
				// create new node
				Node *newNode = new Node(2);

				//rearrange parents
				if (current->parent != nullptr) {
					current->parent->right = newNode;
					newNode->parent = current->parent;
				}

				//set left - new symbol
				newNode->left = new Node(1, val, newNode);

				// set right - ESC
				newNode->right = current;
				newNode->right->parent = newNode;

				setTopFather(newNode);
				
				
				// Keep unique ESC in queue #2
				// if ESC is first 
				if (huff_queue.front()->ch == "ESC")
					huff_queue.pop();

				huff_queue.push(newNode);
				huff_queue.push(newNode->left);
				huff_queue.push(newNode->right);
				
				
			}

			if (current->left != nullptr) {
				huff_queue.push(current->left);
				bfs.push(current->left);
			}
			if (current->right != nullptr) {
				// Keep unique ESC in queue #1 
				// if ESC is deep
				if (current->right->ch != "ESC")
					huff_queue.push(current->right);
				bfs.push(current->right);
			}

			bfs.pop();
		}

		vector<Node*> vec;
		//Check if tree is good # Faller - Gallagerd statement
		while (!huff_queue.empty()) {
			vec.push_back(huff_queue.front());
			huff_queue.pop();
		}
		
		for (int i = vec.size() - 1; i >= 1; --i) {
			if (vec[i - 1]->quantity < vec[i]->quantity ) {
				for (int j = i - 1; j >= 0; --j) {
					if (vec[i]->quantity <= vec[j]->quantity) {
						swapNodes(vec[i], vec[j + 1]);
						swap(vec[i], vec[j + 1]);
						incQuantities(vec[i]);
						break;
					}
				}
			}
		}
	}

	string getEncodedSymbol(string symbol, Node *node, bool ESC = true) {
		Node *runner = node;
		string encodedSymbol = "";
		while (runner->parent != nullptr) {
			if (runner->parent->left == runner)
				encodedSymbol += "0";
			else encodedSymbol += "1";
			runner = runner->parent;
		}

		reverse(encodedSymbol.begin(), encodedSymbol.end());

		if (ESC == true)
			// "0" + 
			encodedSymbol += bitset<7>((int)symbol[0]).to_string();
		return encodedSymbol;
	}
	void swapNodes(Node* n1, Node *n2) {
		Node *n1p = n1->parent;
		Node *n2p = n2->parent;
		n1->parent = n2p;
		n2->parent = n1p;

		if (n1p->left == n1)
			n1p->left = n2;
		else 
			n1p->right = n2;
			
		if (n2p->left == n2)
			n2p->left = n1;
		else
			n2p->right = n1;
	}

	void setTopFather(Node *node)
	{
		Node *runner = node;
		while (runner->parent != nullptr)
			runner = runner->parent;
		root = runner;
	}

	void incQuantities(Node *node) {
		Node *runner = node;
		while (runner->parent != nullptr) {
			runner = runner->parent;
			runner->quantity += 1;
		}
	}
};


int main()
{
	char ch;
	fstream fin("file.txt", fstream::in);
	ofstream sfin("file.enc");
	HuffmanTree tree_encode;
	HuffmanTree tree_decode;
	HuffmanTree tree_decode_file;
	while (fin >> noskipws >> ch) {
		//cout << ch;
		tree_encode.encode(string(1, ch));
		sfin << buffer;
		//cout << (buffer) << endl;
		tree_decode.decode(buffer);
	}
	sfin.close();
	fin.close();

	cout << "\n---\n";

	ifstream f("file.enc");
	stringstream stream;
	stream << f.rdbuf();
	tree_decode_file.decodeFile(stream.str());

	int breaker;
	cin >> breaker;
    return 0;
}

