package stress;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.support.ui.Select;
 
public class StressTest_01 {
 
public static void main(String[] args) {
   
   WebDriver driver = new FirefoxDriver();

   driver.get("http://tscontentcatqa.wsrlab:8080/coreui/");
  
   //Sleeping for 5 secs for the URL to load completely
   try {
	Thread.sleep(5000);
} catch (InterruptedException e) {
	// TODO Auto-generated catch block
	e.printStackTrace();
}
   
   //Find username box and type 'user2' in it
   WebElement uname = driver.findElement(By.className("gwt-TextBox"));
   uname.sendKeys("user2");
   
   //Find oassword box and type 'smartfilter' in it
   WebElement pwd = driver.findElement(By.className("gwt-PasswordTextBox"));
   pwd.sendKeys("smartfilter");
   
   //Selecting WAUI in drop down
   WebElement waui = driver.findElement(By.className("gwt-ListBox"));
   waui.sendKeys("WAUI");
   
   //Clicking on Login button
   WebElement login = driver.findElement(By.className("gwt-Button"));
   login.click();
   
   //Waiting for 5 secs for URL to load
   try {
		Thread.sleep(5000);
	} catch (InterruptedException e) {
		// TODO Auto-generated catch block
		e.printStackTrace();
	}
   Select dropdown=new Select(driver.findElement(By.xpath("/html/body/div[4]/div[2]/div/div/div[2]/form/table/tbody/tr/td[5]/div/select")));
   WebElement dd=dropdown.getFirstSelectedOption();
   dropdown.selectByValue("10");
   
   //Find Search button and click on it multiple times
   WebElement search = driver.findElement(By.xpath("/html/body/div[4]/div[2]/div/div/div[2]/form/table/tbody/tr/td[6]/button"));
   search.click();
  for(int i=0;i<50;i++)
   {
	   search.click();
	   System.out.println("CLick "+ i+1);
	   
   }
   
   //Closing the browser and killing the process
   for(int i=0;i<100;i++)
   {
	   try {
		Thread.sleep(1000);
	} catch (InterruptedException e) {
		// TODO Auto-generated catch b
		}
	   System.out.println(i+1);
	   
	   
	   
	 }
   
   try{
   WebElement load=driver.findElement(By.xpath("/html/body/div[4]/div[2]/div/div/div[7]/div/div[2]/div/div[3]/div/div[2]/div/div/table/tbody/tr/td[2]/div"));
   }
   
   catch(Exception e)
   {
	   
	   System.out.println("Couldnot load URLs due to multiple clicks");
   }
   
   finally{
   driver.close();
   driver.quit();
   }
  }
 
}