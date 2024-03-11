use clap::Parser;
use itertools::Itertools;
use rand::seq::SliceRandom;
use rand::thread_rng;
use rayon::prelude::*;
use std::{
    collections::{HashMap, HashSet},
    error::Error,
    fs::File,
    io::Write,
    net::{IpAddr, Ipv4Addr},
    os::unix::fs::PermissionsExt,
    path::PathBuf,
    sync::{Arc, RwLock},
    time::Duration,
};
use tracert::trace::Tracer;

/// Trace the routes of a network and store the results as a graph
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Input CSV file containing the IP ranges
    #[arg(short, long)]
    input_path: PathBuf,

    /// Output directory to save the results
    #[arg(short, long)]
    output_path: PathBuf,
}

fn main() {
    let args = Args::parse();
    run(args.input_path, args.output_path).unwrap();
}

fn run(input_path: PathBuf, output_path: PathBuf) -> Result<(), Box<dyn Error>> {
    let edges = Arc::new(RwLock::new(
        read_hashmap_from_json_file(output_path.clone()).unwrap_or_default(),
    ));
    let done = Arc::new(RwLock::new(
        read_hashset_from_csv_file(output_path.clone()).unwrap_or_default(),
    ));
    let mut rdr = csv::Reader::from_path(input_path)?;
    let mut ips = rdr
        .records()
        .map_ok(|record| {
            let start = parse_ip(&record[0]);
            let end = parse_ip(&record[1]);
            (start, end)
        })
        .flatten()
        .collect_vec();
    ips.shuffle(&mut thread_rng());
    ips.truncate(200);
    ips.par_iter()
        .enumerate()
        .for_each(|(i, (start_ip, end_ip))| {
            let mut ips = (*start_ip..*end_ip).collect_vec();
            ips.shuffle(&mut thread_rng());
            ips.truncate(10);
            for ip in ips {
                if done.read().unwrap().contains(&ip.into()) {
                    continue;
                }
                println!("{}-Tracing: {:?}", i, ip);
                let ip = ip.to_owned();
                let mut tracer = Tracer::new(ip.into()).unwrap();
                tracer.trace_timeout = Duration::from_secs(2);
                tracer.receive_timeout = Duration::from_secs(1);
                if let Ok(hops) = tracer.trace() {
                    let mut prev: IpAddr = ip.into();
                    for node in hops.nodes.iter() {
                        let mut outer_map = edges.write().unwrap();
                        let inner_map = outer_map.entry(node.ip_addr).or_default();
                        *inner_map.entry(prev).or_default() += 1;
                        prev = node.ip_addr;
                    }
                    done.write().unwrap().insert(ip.into());
                    println!("{}-{} Done: {:?}", i, hops.nodes.len(), ip);
                }
            }
        });

    write_hashmap_to_json_file(&edges.read().unwrap(), output_path.clone()).unwrap();
    write_hashet_to_csv_file(&done.read().unwrap(), output_path).unwrap();

    Ok(())
}

fn read_hashmap_from_json_file(
    file_path: PathBuf,
) -> Result<HashMap<IpAddr, HashMap<IpAddr, usize>>, serde_json::Error> {
    let file_path = file_path.join("edges.json");
    let file = File::open(file_path).expect("Failed to open file");
    let data: HashMap<IpAddr, HashMap<IpAddr, usize>> = serde_json::from_reader(file)?;
    Ok(data)
}

fn write_hashmap_to_json_file(
    data: &HashMap<IpAddr, HashMap<IpAddr, usize>>,
    file_path: PathBuf,
) -> Result<(), serde_json::Error> {
    let file_path = file_path.join("edges.json");
    let json_str = serde_json::to_string(&data)?;
    let mut file = File::create(file_path).expect("Failed to create file");
    file.write_all(json_str.as_bytes())
        .expect("Failed to write to file");
    let _ = file.set_permissions(std::fs::Permissions::from_mode(0o777));

    Ok(())
}

fn read_hashset_from_csv_file(file_path: PathBuf) -> Result<HashSet<IpAddr>, serde_json::Error> {
    let file_path = file_path.join("done.csv");
    let file = File::open(file_path).expect("Failed to open file");
    let data: HashSet<IpAddr> = serde_json::from_reader(file)?;
    Ok(data)
}

fn write_hashet_to_csv_file(
    data: &HashSet<IpAddr>,
    file_path: PathBuf,
) -> Result<(), serde_json::Error> {
    let file_path = file_path.join("done.csv");
    let mut buff = String::new();
    for ip in data.iter() {
        buff.push_str(&format!("{}\n", ip));
    }
    let mut file = File::create(file_path).expect("Failed to create file");
    file.write_all(buff.as_bytes())
        .expect("Failed to write to file");
    let _ = file.set_permissions(std::fs::Permissions::from_mode(0o777));

    Ok(())
}

fn parse_ip(ip: &str) -> Ipv4Addr {
    let ip: Vec<&str> = ip.split('.').collect();
    let ip: [u8; 4] = ip
        .iter()
        .map(|it| it.parse::<u8>().unwrap())
        .collect_vec()
        .try_into()
        .unwrap();

    Ipv4Addr::from(ip)
}
