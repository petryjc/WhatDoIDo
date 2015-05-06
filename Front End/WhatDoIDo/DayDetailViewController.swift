//
//  DayDetailViewController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 1/29/15.
//  Copyright (c) 2015 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit

class DayDetailViewController: UIViewController, UITableViewDelegate {
    @IBOutlet weak var dateLabel : UILabel!
    @IBOutlet var dayDetailTableView : UITableView!
    
    var date : CVDate?
    var suggestionList : [SuggestionModel]?
    var del = UIApplication.sharedApplication().delegate as AppDelegate
    
    
    
    
    func tableView(suggestionTableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        println("MEOWMEOWMEOWMEOW")
        if let count = self.suggestionList?.count {
            println(count);
            return count;
        } else {
            return 0;
        }
    }
    
    func tableView(suggestionTableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        
        var cell:UITableViewCell = self.dayDetailTableView!.dequeueReusableCellWithIdentifier("cell") as UITableViewCell
        
        //var cell = UITableViewCell(style: UITableViewCellStyle.Value2, reuseIdentifier: nil);
        
        if let name = self.suggestionList?[indexPath.row].getName() {
            var time = self.suggestionList?[indexPath.row].getStartTime()
            var nsTime = time! as NSString
            cell.textLabel.text = nsTime.substringWithRange(NSRange(location: 11, length: 5)) + " - " + name
        }
        return cell
    }
    
    func tableView(suggestionTableView: UITableView!, didSelectRowAtIndexPath indexPath: NSIndexPath!) {
        println(self.suggestionList![indexPath.row]) //Actually do something with a selected suggestion here
        del.suggestionModel = self.suggestionList![indexPath.row]
        performSegueWithIdentifier("suggestionSegue", sender: self);
    }
    
    
    
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.dayDetailTableView.registerClass(UITableViewCell.self, forCellReuseIdentifier: "cell")
        println(suggestionList)
        // Do any additional setup after loading the view, typically from a nib.
        refreshUI();
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func refreshUI() {
        var month = intToMonth(self.date!.month!)
        self.dateLabel.text = "\(month) \(self.date!.day!), \(self.date!.year!)"
    }
    
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {
        if (segue.identifier == "suggestionSegue") {
            var vc = segue.destinationViewController as SuggestionViewController
            vc.pageState = 0
            vc.originView = 1
            vc.dayDetailInfo = self.suggestionList
            vc.dayDetailDate = self.date
        }
    }
    
    func intToMonth(index: Int) -> String {
        switch index {
            case 1:
                return "January"
            case 2:
                return "February"
            case 3:
                return "March"
            case 4:
                return "April"
            case 5:
                return "May"
            case 6:
                return "June"
            case 7:
                return "July"
            case 8:
                return "August"
            case 9:
                return "September"
            case 10:
                return "October"
            case 11:
                return "November"
            case 12:
                return "December"
            default:
                return "Unknown"
        }
    }
}